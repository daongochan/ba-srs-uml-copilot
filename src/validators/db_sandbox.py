import functools
import re
import sqlite3
from typing import Dict, Any, List, Optional
import sqlglot
from sqlglot import exp

from src.utils.security import MAX_SQL_DDL_LENGTH, MAX_SQL_STATEMENTS

# Regex phát hiện câu lệnh bị cấm có thể phá vỡ phạm vi SQLite sandbox
_DANGEROUS_SQL_PATTERN = re.compile(
    r"\b(ATTACH(?:\s+DATABASE)?|DETACH(?:\s+DATABASE)?|VACUUM\s+INTO|load_extension|PRAGMA\s+writable_schema)\b",
    re.IGNORECASE,
)

# Pre-compiled regexes cho chuẩn hóa cú pháp SQLite DDL
_DEFAULT_UUID_REGEX = re.compile(
    r'DEFAULT\s+\(?\s*(?:uuid_generate_v4|gen_random_uuid)\s*\(\s*\)\s*\)?',
    re.IGNORECASE,
)
_DEFAULT_NOW_REGEX = re.compile(
    r'DEFAULT\s+\(?\s*now\s*\(\s*\)\s*\)?',
    re.IGNORECASE,
)
_NULLS_ORDER_REGEX = re.compile(
    r'\bNULLS\s+(?:LAST|FIRST)\b',
    re.IGNORECASE,
)
_CONCURRENTLY_REGEX = re.compile(
    r'\bCONCURRENTLY\b',
    re.IGNORECASE,
)
_USING_INDEX_REGEX = re.compile(
    r'\bUSING\s+(?:BTREE|HASH|GIN|GIST)\b',
    re.IGNORECASE,
)
_TRAILING_COMMA_REGEX = re.compile(r',\s*\)')
_MARKDOWN_FENCE_START_REGEX = re.compile(r"^```(?:sql)?\s*\n?", re.IGNORECASE)
_MARKDOWN_FENCE_END_REGEX = re.compile(r"\n?```\s*$")


@functools.lru_cache(maxsize=256)
def _sanitize_ddl_for_sqlite(sql_ddl: str) -> str:
    """Loại bỏ hoặc thay thế các hàm/cú pháp đặc thù của Postgres để chạy an toàn trên SQLite (kèm LRU Cache)."""
    sanitized = sql_ddl

    # 1. Loại bỏ các hàm DEFAULT đặc thù không được hỗ trợ trong SQLite
    sanitized = _DEFAULT_UUID_REGEX.sub('', sanitized)

    # 2. Chuẩn hóa now() sang CURRENT_TIMESTAMP
    sanitized = _DEFAULT_NOW_REGEX.sub('DEFAULT CURRENT_TIMESTAMP', sanitized)

    # 3. Loại bỏ NULLS LAST và NULLS FIRST trong định nghĩa chỉ mục
    sanitized = _NULLS_ORDER_REGEX.sub('', sanitized)

    # 4. Loại bỏ các mệnh đề chỉ mục đặc thù Postgres như USING (BTREE|HASH|GIN|GIST) hoặc CONCURRENTLY
    sanitized = _CONCURRENTLY_REGEX.sub('', sanitized)
    sanitized = _USING_INDEX_REGEX.sub('', sanitized)

    # 5. Dọn dẹp dấu phẩy thừa trước dấu đóng ngoặc
    sanitized = _TRAILING_COMMA_REGEX.sub(')', sanitized)
    return sanitized.strip()



def execute_and_audit_ddl(sql_code: str) -> Dict[str, Any]:
    """Thực thi đoạn mã SQL DDL trong cơ sở dữ liệu SQLite in-memory (:memory:)
    và thực hiện kiểm toán vật lý chuyên sâu: B-Tree Leftmost-Prefix Indexing,
    kiểm tra Khóa chính (Primary Key), phát hiện Khóa ngoại chưa đánh chỉ mục (Unindexed FKs)
    và tự động sinh kịch bản index khắc phục.

    Args:
        sql_code: Chuỗi câu lệnh SQL DDL (hỗ trợ cả markdown fence).

    Returns:
        dict: Chứa:
            - execution_success (bool): Kết quả khởi tạo các bảng thành công.
            - table_count (int): Số lượng bảng vật lý được tạo thành công.
            - total_foreign_keys (int): Tổng số ràng buộc khóa ngoại được thiết lập.
            - total_indexes_created (int): Tổng số Index vật lý hiện có trong schema.
            - tables_metadata (List[dict]): Danh sách thông tin chi tiết từng bảng.
            - tables_without_pk (List[str]): Danh sách tên các bảng bị thiếu Primary Key.
            - unindexed_foreign_keys (List[dict]): Danh sách các khóa ngoại thiếu B-Tree index.
            - recommended_index_script (str): Chuỗi các lệnh CREATE INDEX được đề xuất.
            - performance_health_score (int): Điểm sức khỏe hiệu năng CSDL (0-100).
            - warnings (List[str]): Cảnh báo chỉ mục nếu có câu lệnh index không tương thích.
            - error_message (str | None): Thông báo lỗi nếu thất bại khi tạo bảng.
    """
    default_failure: Dict[str, Any] = {
        "execution_success": False,
        "table_count": 0,
        "total_foreign_keys": 0,
        "total_indexes_created": 0,
        "tables_metadata": [],
        "tables_without_pk": [],
        "unindexed_foreign_keys": [],
        "recommended_index_script": "",
        "performance_health_score": 0,
        "warnings": [],
        "error_message": None,
    }

    if not sql_code or not sql_code.strip():
        res = default_failure.copy()
        res["error_message"] = "Đoạn mã SQL trống."
        return res

    if len(sql_code) > MAX_SQL_DDL_LENGTH:
        res = default_failure.copy()
        res["error_message"] = f"Mã SQL DDL vượt quá giới hạn an toàn cho phép ({MAX_SQL_DDL_LENGTH:,} ký tự)."
        return res

    if _DANGEROUS_SQL_PATTERN.search(sql_code):
        res = default_failure.copy()
        res["error_message"] = "Phát hiện câu lệnh hoặc từ khóa nguy hiểm bị cấm trong SQLite Sandbox (ATTACH/DETACH/VACUUM INTO/load_extension)."
        return res

    # Loại bỏ markdown fences
    cleaned_sql = sql_code.strip()
    cleaned_sql = _MARKDOWN_FENCE_START_REGEX.sub("", cleaned_sql).strip()
    cleaned_sql = _MARKDOWN_FENCE_END_REGEX.sub("", cleaned_sql).strip()


    if not cleaned_sql:
        res = default_failure.copy()
        res["error_message"] = "Đoạn mã SQL trống sau khi làm sạch markdown."
        return res

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
        res = default_failure.copy()
        res["error_message"] = "Không tìm thấy câu lệnh CREATE TABLE hợp lệ nào để thực thi."
        return res

    if len(table_statements) + len(index_statements) > MAX_SQL_STATEMENTS:
        res = default_failure.copy()
        res["error_message"] = f"Số lượng câu lệnh SQL DDL vượt quá giới hạn an toàn (tối đa {MAX_SQL_STATEMENTS} câu lệnh)."
        return res

    # 2. Thực thi trong SQLite in-memory sandbox
    conn = None
    try:
        conn = sqlite3.connect(":memory:")
        step_counter = 0
        MAX_PROGRESS_STEPS = 50_000

        def _sandbox_progress_handler() -> int:
            nonlocal step_counter
            step_counter += 1
            if step_counter > MAX_PROGRESS_STEPS:
                return 1
            return 0

        conn.set_progress_handler(_sandbox_progress_handler, 100)
        cursor = conn.cursor()

        # BƯỚC A: Thực thi toàn bộ câu lệnh CREATE TABLE
        for stmt in table_statements:
            cursor.execute(stmt)

        # BƯỚC B: Thực thi các câu lệnh CREATE INDEX trong khối try...except riêng biệt
        index_warnings: List[str] = []
        for idx_stmt in index_statements:
            try:
                cursor.execute(idx_stmt)
            except Exception as idx_err:
                index_warnings.append(f"Chỉ mục '{idx_stmt[:50]}...': {str(idx_err)}")

        # 3. Trích xuất danh sách bảng vật lý đã khởi tạo thành công
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            res = default_failure.copy()
            res["warnings"] = index_warnings
            res["error_message"] = "Không có bảng nào được khởi tạo trong bộ nhớ RAM."
            return res

        # 4. Kiểm toán chuyên sâu: Khóa chính (PK), Khóa ngoại (FK) & Leftmost Prefix B-Tree Coverage
        tables_metadata: List[Dict[str, Any]] = []
        total_foreign_keys = 0
        tables_without_pk: List[str] = []
        unindexed_foreign_keys: List[Dict[str, Any]] = []
        seen_unindexed_keys = set()

        for tbl in tables:
            safe_tbl = tbl.replace('"', '""')
            # Lấy thông tin cột: cid, name, type, notnull, dflt_value, pk
            cursor.execute(f'PRAGMA table_info("{safe_tbl}");')
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

            # Kiểm tra xem bảng có Primary Key hay không
            has_primary_key = any(r[5] > 0 for r in col_rows)
            if not has_primary_key:
                tables_without_pk.append(tbl)

            # Quy tắc Leftmost Prefix B-Tree:
            # 1. Cột Primary Key đứng đầu (pk == 1) hoặc single PK
            leftmost_indexed_cols = set()
            for r in col_rows:
                if r[5] == 1:
                    leftmost_indexed_cols.add(r[1])

            # 2. Cột đứng ở vị trí đầu tiên (seqno == 0) của mọi Index trên bảng (PRAGMA index_list & index_info)
            cursor.execute(f'PRAGMA index_list("{safe_tbl}");')
            idx_rows = cursor.fetchall()
            for idx_r in idx_rows:
                idx_name = idx_r[1]
                safe_idx = idx_name.replace('"', '""')
                cursor.execute(f'PRAGMA index_info("{safe_idx}");')
                info_rows = cursor.fetchall()
                for info_r in info_rows:
                    seqno = info_r[0]
                    col_name = info_r[2]
                    if seqno == 0 and col_name:
                        leftmost_indexed_cols.add(col_name)

            # Lấy thông tin khóa ngoại: id, seq, table, from, to, on_update, on_delete, match
            cursor.execute(f'PRAGMA foreign_key_list("{safe_tbl}");')
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

            # Đối chiếu từng cột FK với tập cột đã có B-Tree index (leftmost prefix)
            for fk in foreign_keys:
                from_col = fk["from_column"]
                if from_col and from_col not in leftmost_indexed_cols:
                    dedup_key = (tbl, from_col)
                    if dedup_key not in seen_unindexed_keys:
                        seen_unindexed_keys.add(dedup_key)
                        unindexed_foreign_keys.append({
                            "table": tbl,
                            "fk_column": from_col,
                            "referenced_table": fk["target_table"],
                            "suggested_ddl": f"CREATE INDEX IF NOT EXISTS idx_{tbl}_{from_col} ON {tbl} ({from_col});",
                        })

            tables_metadata.append({
                "table_name": tbl,
                "has_primary_key": has_primary_key,
                "column_count": len(columns),
                "columns": columns,
                "foreign_key_count": len(foreign_keys),
                "foreign_keys": foreign_keys,
                "referenced_tables": referenced_tables,
                "leftmost_indexed_columns": sorted(list(leftmost_indexed_cols)),
            })

        # Tổng số Index vật lý hiện có (không tính auto-indexes nội bộ của SQLite)
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
        total_indexes_created = cursor.fetchone()[0]

        # Chuỗi script đề xuất tạo index
        recommended_index_script = "\n".join(item["suggested_ddl"] for item in unindexed_foreign_keys)

        # Điểm sức khỏe hiệu năng CSDL: 100 - len(tables_without_pk)*25 - len(unindexed_foreign_keys)*10
        raw_score = 100 - len(tables_without_pk) * 25 - len(unindexed_foreign_keys) * 10
        performance_health_score = max(0, min(100, raw_score))

        return {
            "execution_success": True,
            "table_count": len(tables_metadata),
            "total_foreign_keys": total_foreign_keys,
            "total_indexes_created": total_indexes_created,
            "tables_metadata": tables_metadata,
            "tables_without_pk": tables_without_pk,
            "unindexed_foreign_keys": unindexed_foreign_keys,
            "recommended_index_script": recommended_index_script,
            "performance_health_score": performance_health_score,
            "warnings": index_warnings,
            "error_message": None,
        }

    except (sqlite3.Error, Exception) as db_err:
        res = default_failure.copy()
        res["error_message"] = f"Lỗi thực thi SQLite in-memory: {str(db_err)}"
        return res
    finally:
        if conn:
            conn.close()
