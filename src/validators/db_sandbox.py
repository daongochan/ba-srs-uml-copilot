"""In-memory SQLite execution sandbox for physical database validation."""

import re
import sqlite3
from typing import Dict, Any, List, Optional
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError, SqlglotError


def _sanitize_ddl_for_sqlite(sql_ddl: str) -> str:
    """Loại bỏ hoặc thay thế các hàm/cú pháp đặc thù của Postgres để chạy an toàn trên SQLite."""
    # Xóa các hàm DEFAULT không được hỗ trợ trong SQLite
    sanitized = re.sub(
        r'DEFAULT\s+\(?\s*(?:uuid_generate_v4|gen_random_uuid)\s*\(\s*\)\s*\)?',
        '',
        sql_ddl,
        flags=re.IGNORECASE,
    )
    # Chuẩn hóa now() sang CURRENT_TIMESTAMP
    sanitized = re.sub(
        r'DEFAULT\s+\(?\s*now\s*\(\s*\)\s*\)?',
        'DEFAULT CURRENT_TIMESTAMP',
        sanitized,
        flags=re.IGNORECASE,
    )
    # Dọn dẹp dấu phẩy thừa trước dấu đóng ngoặc
    sanitized = re.sub(r',\s*\)', ')', sanitized)
    return sanitized.strip()


def execute_and_audit_ddl(sql_code: str) -> Dict[str, Any]:
    """Thực thi toàn bộ đoạn mã SQL DDL trong cơ sở dữ liệu SQLite in-memory (:memory:)

    nhằm kiểm định tính khả thi vật lý, cấu trúc các bảng và các ràng buộc khóa ngoại (FK).

    Args:
        sql_code: Chuỗi câu lệnh SQL DDL (có thể có markdown fence).

    Returns:
        dict: Chứa:
            - execution_success (bool): Kết quả thực thi thành công hay không.
            - table_count (int): Số lượng bảng vật lý được tạo thành công.
            - total_foreign_keys (int): Tổng số ràng buộc khóa ngoại được thiết lập.
            - tables_metadata (List[dict]): Danh sách thông tin chi tiết từng bảng.
            - error_message (str | None): Thông báo lỗi nếu thất bại.
    """
    if not sql_code or not sql_code.strip():
        return {
            "execution_success": False,
            "table_count": 0,
            "total_foreign_keys": 0,
            "tables_metadata": [],
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
            "error_message": "Đoạn mã SQL trống sau khi làm sạch markdown.",
        }

    # 1. Phân tích AST và trích xuất các câu lệnh CREATE TABLE / CREATE INDEX
    create_statements: List[str] = []
    try:
        try:
            expressions = sqlglot.parse(cleaned_sql, read="postgres")
        except Exception:
            expressions = sqlglot.parse(cleaned_sql)

        for expr in expressions:
            if expr is None:
                continue
            if isinstance(expr, exp.Create):
                # Dịch sang dialect sqlite
                sqlite_sql = expr.sql(dialect="sqlite")
                sanitized_sql = _sanitize_ddl_for_sqlite(sqlite_sql)
                if sanitized_sql:
                    create_statements.append(sanitized_sql)
            elif "CREATE TABLE" in expr.sql().upper():
                sqlite_sql = expr.sql(dialect="sqlite")
                sanitized_sql = _sanitize_ddl_for_sqlite(sqlite_sql)
                if sanitized_sql:
                    create_statements.append(sanitized_sql)
    except Exception:
        # Nếu sqlglot gặp sự cố phân tích, fallback tách thủ công theo dấu chấm phẩy
        statements = [stmt.strip() for stmt in cleaned_sql.split(";") if stmt.strip()]
        for stmt in statements:
            if "CREATE TABLE" in stmt.upper() or "CREATE INDEX" in stmt.upper():
                create_statements.append(_sanitize_ddl_for_sqlite(stmt))

    if not create_statements:
        return {
            "execution_success": False,
            "table_count": 0,
            "total_foreign_keys": 0,
            "tables_metadata": [],
            "error_message": "Không tìm thấy câu lệnh CREATE TABLE hợp lệ nào để thực thi.",
        }

    # 2. Thực thi trong SQLite in-memory sandbox
    conn = None
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        for stmt in create_statements:
            cursor.execute(stmt)

        # 3. Trích xuất danh sách bảng vật lý đã khởi tạo
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            return {
                "execution_success": False,
                "table_count": 0,
                "total_foreign_keys": 0,
                "tables_metadata": [],
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

        return {
            "execution_success": True,
            "table_count": len(tables_metadata),
            "total_foreign_keys": total_foreign_keys,
            "tables_metadata": tables_metadata,
            "error_message": None,
        }

    except (sqlite3.Error, Exception) as db_err:
        return {
            "execution_success": False,
            "table_count": 0,
            "total_foreign_keys": 0,
            "tables_metadata": [],
            "error_message": f"Lỗi thực thi SQLite in-memory: {str(db_err)}",
        }
    finally:
        if conn:
            conn.close()
