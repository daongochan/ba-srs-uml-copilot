"""Syntax validator for Mermaid diagrams and SQL DDL scripts."""

import re
from typing import Tuple, List
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError, SqlglotError


def clean_and_validate_mermaid(code: str) -> str:
    """Loại bỏ các thẻ markdown thừa (như ```mermaid và ```) và kiểm tra

    tính hợp lệ của từ khóa đầu tiên (sequenceDiagram hoặc erDiagram).

    Args:
        code: Đoạn mã Mermaid (có thể chứa markdown code block)

    Returns:
        str: Đoạn mã Mermaid đã được làm sạch và chuẩn hóa.

    Raises:
        ValueError: Nếu mã rỗng hoặc từ khóa đầu tiên không phải sequenceDiagram / erDiagram.
    """
    if not code or not code.strip():
        raise ValueError("Mã Mermaid không được để trống.")

    cleaned = code.strip()

    # Loại bỏ code block mở đầu: ```mermaid hoặc ```
    cleaned = re.sub(r"^```(?:mermaid)?\s*\n?", "", cleaned, flags=re.IGNORECASE).strip()

    # Loại bỏ code block kết thúc: ```
    cleaned = re.sub(r"\n?```\s*$", "", cleaned).strip()

    # Tìm dòng lệnh đầu tiên không phải comment (%%) và không rỗng
    lines = cleaned.splitlines()
    first_keyword = None
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("%%"):
            continue
        first_keyword = stripped_line.split()[0]
        break

    valid_keywords = {"sequenceDiagram", "erDiagram"}
    if not first_keyword:
        raise ValueError("Mã Mermaid không chứa cú pháp hợp lệ.")

    # Kiểm tra từ khóa đầu tiên (hỗ trợ case-insensitive và chuẩn hóa)
    matched_keyword = None
    for valid_kw in valid_keywords:
        if first_keyword.lower() == valid_kw.lower():
            matched_keyword = valid_kw
            break

    if not matched_keyword:
        raise ValueError(
            f"Cú pháp Mermaid không hợp lệ: Từ khóa đầu tiên phải là 'sequenceDiagram' hoặc 'erDiagram' "
            f"(nhận được: '{first_keyword}')."
        )

    return cleaned


def validate_sql_ddl(sql_code: str, dialect: str = "postgres") -> Tuple[bool, str]:
    """Phân tích cú pháp (parse) đoạn mã SQL DDL do AI sinh ra bằng thư viện sqlglot

    nhằm đảm bảo câu lệnh CREATE TABLE không bị lỗi cú pháp trước khi hiển thị.

    Args:
        sql_code: Đoạn mã SQL DDL (có thể có markdown fence).
        dialect: Hệ quản trị CSDL mục tiêu (mặc định 'postgres', có thể là 'mysql', 'sqlite').

    Returns:
        tuple[bool, str]: (is_valid, message)
    """
    if not sql_code or not sql_code.strip():
        return False, "Đoạn mã SQL trống."

    cleaned_sql = sql_code.strip()

    # Loại bỏ markdown fences nếu có
    cleaned_sql = re.sub(r"^```(?:sql)?\s*\n?", "", cleaned_sql, flags=re.IGNORECASE).strip()
    cleaned_sql = re.sub(r"\n?```\s*$", "", cleaned_sql).strip()

    if not cleaned_sql:
        return False, "Đoạn mã SQL trống sau khi làm sạch markdown."

    try:
        # Thử parse bằng dialect được chỉ định với mức lỗi RAISE
        try:
            expressions = sqlglot.parse(cleaned_sql, read=dialect, error_level=sqlglot.ErrorLevel.RAISE)
        except Exception:
            # Fallback sang generic dialect nếu dialect chỉ định gặp syntax mở rộng
            expressions = sqlglot.parse(cleaned_sql, error_level=sqlglot.ErrorLevel.RAISE)

        if not expressions:
            return False, "Không thể phân tích bất kỳ câu lệnh SQL nào từ đoạn mã."

        # Kiểm tra xem có câu lệnh CREATE TABLE nào không
        create_table_found = False
        for expr in expressions:
            if expr is None:
                continue
            # Kiểm tra dạng AST hoặc chuỗi SQL sinh ra
            if isinstance(expr, exp.Create):
                create_table_found = True
                break
            sql_upper = expr.sql().upper()
            if "CREATE TABLE" in sql_upper:
                create_table_found = True
                break

        if not create_table_found:
            return (
                False,
                "Không tìm thấy câu lệnh 'CREATE TABLE' hợp lệ trong đoạn mã SQL DDL.",
            )

        return True, "Cú pháp SQL DDL hợp lệ."

    except (ParseError, SqlglotError) as err:
        return False, f"Lỗi cú pháp SQL: {str(err)}"
    except Exception as err:
        return False, f"Lỗi không xác định khi phân tích SQL: {str(err)}"
