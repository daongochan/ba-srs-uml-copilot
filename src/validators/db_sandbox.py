"""In-memory SQLite execution sandbox for physical database validation."""

import re
import sqlite3
from typing import Dict, Any, List, Optional
import sqlglot
from sqlglot import exp


def _sanitize_ddl_for_sqlite(sql_ddl: str) -> str:
    """Loại bỏ hoặc thay thế các hàm/cú pháp đặc thù của Postgres để chạy an toàn trên SQLite."""
    sanitized = sql_ddl

    # 1. Loại bỏ các hàm DEFAULT đặc thù không được hỗ trợ trong SQLite
    sanitized = re.sub(
        r'DEFAULT\s+\(?\s*(?:uuid_generate_v4|gen_random_uuid)\s*\(\s*\)\s*\)?',
        '',
        sanitized,
        flags=re.IGNORECASE,
    )

    # 2. Chuẩn hóa now() sang CURRENT_TIMESTAMP
    sanitized = re.sub(
        r'DEFAULT\s+\(?\s*now\s*\(\s*\)\s*\)?',
        'DEFAULT CURRENT_TIMESTAMP',
        sanitized,
        flags=re.IGNORECASE,
    )

    # 3. Loại bỏ NULLS LAST và NULLS FIRST trong định nghĩa chỉ mục
    sanitized = re.sub(
        r'\bNULLS\s+(?:LAST|FIRST)\b',
        '',
        sanitized,
        flags=re.IGNORECASE,
    )

    # 4. Loại bỏ các mệnh đề chỉ mục đặc thù Postgres như USING (BTREE|HASH|GIN|GIST) hoặc CONCURRENTLY
    sanitized = re.sub(
        r'\bCONCURRENTLY\b',
        '',
        sanitized,
        flags=re.IGNORECASE,
    )
    sanitized = re.sub(
        r'\bUSING\s+(?:BTREE|HASH|GIN|GIST)\b',
        '',
        sanitized,
        flags=re.IGNORECASE,
    )

    # 5. Dọn dẹp dấu phẩy thừa trước dấu đóng ngoặc
    sanitized = re.sub(r',\s*\)', ')', sanitized)
    return sanitized.strip()


def execute_and_audit_ddl(sql_code: str) -> Dict[str, Any]:
    """Thực thi đoạn mã SQL DDL trong cơ sở dữ liệu SQLite in-memory (:memory:)
    với quy trình phân tách độc lập giữa CREATE TABLE và CREATE INDEX nhằm đảm bảo
    kiểm toán chính xác số bảng và khóa ngoại ngay cả khi có chỉ mục Postgres đặc thù.

    Args:
        sql_code: Chuỗi câu lệnh SQL DDL (hỗ trợ cả markdown fence).

    Returns:
        dict: Chứa:
            - execution_success (bool): Kết quả khởi tạo các bảng thành công.
            - table_count (int): Số lượng bảng vật lý được tạo thành công.
            - total_foreign_keys (int): Tổng số ràng buộc khóa ngoại được thiết lập.
            - tables_metadata (List[dict]): Danh sách thông tin chi tiết từng bảng.
            - warnings (List[str]): Cảnh báo chỉ mục nếu có câu lệnh index không tương thích.
            - error_message (str | None): Thông báo lỗi nếu thất bại khi tạo bảng.
    """
    if not sql_code or not sql_code.strip():
        return {
            "execution_success": False,
            "table_count": 0,
            "total_foreign_keys": 0,
            "tables_metadata": [],
            "warnings": [],
            "error_message": "Đoạn mã SQL trống.",
        }

    # Loại bỏ markdown fences
    cleaned_sql = sql_code.strip()
    cleaned_sql = re.sub(r"^```(?:sql)?\s*\n?", "", cleaned_sql, flags=re.IGNORECASE).strip()
    cleaned_sql = re.sub(r"\n?```\s*$", "", cleaned_sql).strip()

    if not cleaned_sql:
        return {
            "execution_success": False,
            "table_count": 0,
            "total_foreign_keys": 0,
            "tables_metadata": [],
            "warnings": [],
            "error_message": "Đoạn mã SQL trống sau khi làm sạch markdown.",
        }

    # 1. Phân tách câu lệnh CREATE TABLE và CREATE INDEX
    table_statements: List[str] = []
    index_statements: List[str] = []

    try:
        try:
            expressions = sqlglot.parse(cleaned_sql, read="postgres")
        except Exception:
            expressions = sqlglot.parse(cleaned_sql)

        for expr in expressions:
            if expr is None:
                continue
            if isinstance(expr, exp.Create):
                kind = str(getattr(expr, "kind", "")).upper()
                sqlite_sql = expr.sql(dialect="sqlite")
                sanitized_sql = _sanitize_ddl_for_sqlite(sqlite_sql)
                if not sanitized_sql:
                    continue
                if kind == "TABLE" or "CREATE TABLE" in expr.sql().upper():
                    table_statements.append(sanitized_sql)
                elif kind == "INDEX" or "CREATE INDEX" in expr.sql().upper():
                    index_statements.append(sanitized_sql)
            elif "CREATE TABLE" in expr.sql().upper():
                sqlite_sql = expr.sql(dialect="sqlite")
                sanitized_sql = _sanitize_ddl_for_sqlite(sqlite_sql)
                if sanitized_sql:
                    table_statements.append(sanitized_sql)
            elif "CREATE INDEX" in expr.sql().upper():
                sqlite_sql = expr.sql(dialect="sqlite")
                sanitized_sql = _sanitize_ddl_for_sqlite(sqlite_sql)
                if sanitized_sql:
                    index_statements.append(sanitized_sql)
    except Exception:
        pass

    # Nếu sqlglot không trích xuất được bảng, dùng fallback tách thủ công theo dấu chấm phẩy
    if not table_statements:
        statements = [stmt.strip() for stmt in cleaned_sql.split(";") if stmt.strip()]
        for stmt in statements:
            stmt_upper = stmt.upper()
            sanitized = _sanitize_ddl_for_sqlite(stmt)
            if not sanitized:
                continue
            if "CREATE TABLE" in stmt_upper:
                table_statements.append(sanitized)
            elif "CREATE INDEX" in stmt_upper or "CREATE UNIQUE INDEX" in stmt_upper:
                index_statements.append(sanitized)

    if not table_statements:
        return {
            "execution_success": False,
            "table_count": 0,
            "total_foreign_keys": 0,
            "tables_metadata": [],
            "warnings": [],
            "error_message": "Không tìm thấy câu lệnh CREATE TABLE hợp lệ nào để thực thi.",
        }

    # 2. Thực thi trong SQLite in-memory sandbox
    conn = None
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # BƯỚC A: Thực thi toàn bộ câu lệnh CREATE TABLE
        for stmt in table_statements:
            cursor.execute(stmt)

        # Trích xuất danh sách bảng vật lý đã khởi tạo thành công
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            return {
                "execution_success": False,
                "table_count": 0,
                "total_foreign_keys": 0,
                "tables_metadata": [],
                "warnings": [],
                "error_message": "Không có bảng nào được khởi tạo trong bộ nhớ RAM.",
            }

        tables_metadata: List[Dict[str, Any]] = []
        total_foreign_keys = 0

        for tbl in tables:
            # Lấy thông tin cột: cid, name, type, notnull, dflt_value, pk
            cursor.execute(f"PRAGMA table_info('{tbl}');")
            col_rows = cursor.fetchall()
            columns = [
                {
                    "name": r[1],
                    "type": r[2],
                    "not_null": bool(r[3]),
                    "primary_key": bool(r[5]),
                }
                for r in col_rows
            ]

            # Lấy thông tin khóa ngoại: id, seq, table, from, to, on_update, on_delete, match
            cursor.execute(f"PRAGMA foreign_key_list('{tbl}');")
            fk_rows = cursor.fetchall()
            foreign_keys = [
                {
                    "from_column": r[3],
                    "target_table": r[2],
                    "target_column": r[4],
                }
                for r in fk_rows
            ]
            referenced_tables = list(dict.fromkeys(r[2] for r in fk_rows))
            total_foreign_keys += len(foreign_keys)

            tables_metadata.append({
                "table_name": tbl,
                "column_count": len(columns),
                "columns": columns,
                "foreign_key_count": len(foreign_keys),
                "foreign_keys": foreign_keys,
                "referenced_tables": referenced_tables,
            })

        # BƯỚC B: Thực thi các câu lệnh CREATE INDEX trong khối try...except riêng biệt
        index_warnings: List[str] = []
        for idx_stmt in index_statements:
            try:
                cursor.execute(idx_stmt)
            except Exception as idx_err:
                index_warnings.append(f"Chỉ mục '{idx_stmt[:50]}...': {str(idx_err)}")

        return {
            "execution_success": True,
            "table_count": len(tables_metadata),
            "total_foreign_keys": total_foreign_keys,
            "tables_metadata": tables_metadata,
            "warnings": index_warnings,
            "error_message": None,
        }

    except (sqlite3.Error, Exception) as db_err:
        return {
            "execution_success": False,
            "table_count": 0,
            "total_foreign_keys": 0,
            "tables_metadata": [],
            "warnings": [],
            "error_message": f"Lỗi thực thi SQLite in-memory: {str(db_err)}",
        }
    finally:
        if conn:
            conn.close()
