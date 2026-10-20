"""Syntax validator for Mermaid diagrams and SQL DDL scripts."""

import re
import unicodedata
from typing import Tuple, List, Optional
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError, SqlglotError


def _slugify_to_id(text: str) -> str:
    """Chuyển đổi văn bản tiếng Việt hoặc có khoảng trắng thành ID tiếng Anh hợp lệ."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_text = ascii_text.replace("đ", "d").replace("Đ", "D")
    clean_id = re.sub(r"[^a-zA-Z0-9_]", "_", ascii_text)
    clean_id = re.sub(r"_+", "_", clean_id).strip("_")
    if not clean_id or clean_id[0].isdigit():
        clean_id = f"P_{clean_id}" if clean_id else "Participant"
    return clean_id


def _clean_erd_attribute_line(line: str) -> str:
    """Xóa kích thước trong ngoặc đơn của kiểu dữ liệu và dấu phẩy thừa ở cuối dòng thuộc tính ERD."""
    stripped = line.strip()
    if not stripped or stripped.startswith("%%"):
        return line

    leading_spaces = len(line) - len(line.lstrip())
    indent = line[:leading_spaces]

    # Kiểm tra chú thích ở cuối dòng: "comment" hoặc 'comment' (có thể có dấu phẩy sau)
    comment_match = re.search(r'([\'"])(.*?)\1\s*,?\s*$', stripped)
    if comment_match:
        comment_text = comment_match.group(2)
        before_comment = stripped[:comment_match.start(0)].rstrip()
        # Xóa kích thước kiểu dữ liệu trong ngoặc: varchar(150) -> varchar, decimal(10, 2) -> decimal
        before_comment = re.sub(r'([a-zA-Z0-9_]+)\s*\([^)]*\)', r'\1', before_comment)
        # Xóa dấu phẩy phân tách giữa các trường
        before_comment = before_comment.replace(',', ' ')
        tokens = before_comment.split()
        cleaned_before = " ".join(tokens)
        return f'{indent}{cleaned_before} "{comment_text}"'
    else:
        # Không có chú thích
        # Xóa dấu phẩy ở cuối dòng
        cleaned = re.sub(r',\s*$', '', stripped)
        # Xóa kích thước kiểu dữ liệu trong ngoặc: varchar(150) -> varchar, decimal(10, 2) -> decimal
        cleaned = re.sub(r'([a-zA-Z0-9_]+)\s*\([^)]*\)', r'\1', cleaned)
        cleaned = cleaned.replace(',', ' ')
        tokens = cleaned.split()
        cleaned_attr = " ".join(tokens)
        return f'{indent}{cleaned_attr}'


def _clean_seq_participant_line(line: str) -> str:
    """Chuẩn hóa dòng khai báo actor/participant trong Sequence Diagram: ID as "Tên Hiển Thị"."""
    stripped = line.strip()
    match = re.match(r"^(actor|participant)\s+(.*)$", stripped, flags=re.IGNORECASE)
    if not match:
        return line

    leading_spaces = len(line) - len(line.lstrip())
    indent = line[:leading_spaces]
    role = match.group(1)
    rest = match.group(2).strip()

    # Trường hợp 1: Có từ khóa " as "
    m_as = re.match(r"^(.*?)\s+as\s+(.*)$", rest, flags=re.IGNORECASE)
    if m_as:
        id_part = m_as.group(1).strip()
        alias_part = m_as.group(2).strip()
        # Nếu id_part có khoảng trắng hoặc ký tự tiếng Việt/non-ASCII -> slugify thành ID hợp lệ
        if " " in id_part or any(ord(c) > 127 for c in id_part):
            id_part = _slugify_to_id(id_part)
        else:
            id_part = id_part.strip('\'"')

        # Đảm bảo tên hiển thị được bọc trong dấu ngoặc kép ""
        if (alias_part.startswith('"') and alias_part.endswith('"')) or (
            alias_part.startswith("'") and alias_part.endswith("'")
        ):
            clean_alias = alias_part[1:-1].strip()
        else:
            clean_alias = alias_part.strip()
        return f'{indent}{role} {id_part} as "{clean_alias}"'

    # Trường hợp 2: Không có " as "
    # Nếu là một định danh ASCII đơn lẻ không khoảng trắng và không ngoặc kép -> giữ nguyên
    if " " not in rest and not any(ord(c) > 127 for c in rest) and not rest.startswith(('"', "'")):
        return line

    # Có khoảng trắng, tiếng Việt hoặc bọc ngoặc kép -> tạo ID và bọc tên hiển thị trong ngoặc kép
    clean_display = rest.strip('\'"')
    clean_id = _slugify_to_id(clean_display)
    return f'{indent}{role} {clean_id} as "{clean_display}"'


def _clean_seq_message_line(line: str) -> str:
    """Loại bỏ dấu chấm phẩy ';' và ngoặc nhọn '{}' trong thông điệp Sequence Diagram."""
    arrow_pattern = r"(->>|-->>|->|-->|-x|--x|-\)|--\))"
    if re.search(arrow_pattern, line) and ":" in line:
        prefix, msg = line.split(":", 1)
        cleaned_msg = msg.replace(";", "").replace("{", "(").replace("}", ")")
        return f"{prefix}:{cleaned_msg}"
    return line


def clean_and_validate_mermaid(code: str, diagram_type: str = "") -> str:
    """Loại bỏ các thẻ markdown thừa (như ```mermaid và ```), unescape ký tự xuống dòng,
    chuẩn hóa cú pháp Mermaid đặc thù (erDiagram, sequenceDiagram) và kiểm tra tính hợp lệ
    của từ khóa đầu tiên.

    Args:
        code: Đoạn mã Mermaid (có thể chứa markdown code block, \\n escape)
        diagram_type: Kiểu sơ đồ ('sequenceDiagram', 'erDiagram', hoặc để trống để tự động nhận diện)

    Returns:
        str: Đoạn mã Mermaid đã được làm sạch và chuẩn hóa triệt để.

    Raises:
        ValueError: Nếu mã rỗng hoặc từ khóa đầu tiên không phải sequenceDiagram / erDiagram.
    """
    if not code or not code.strip():
        raise ValueError("Mã Mermaid không được để trống.")

    # 1. Chuyển đổi các chuỗi \\n bị escape thành ký tự xuống dòng \n thực sự
    cleaned = code.replace("\\r\\n", "\n").replace("\\n", "\n")

    # 2. Loại bỏ hoàn toàn các dòng chứa ```mermaid hoặc ```
    raw_lines = cleaned.splitlines()
    lines = [line for line in raw_lines if "```" not in line]
    cleaned = "\n".join(lines).strip()

    if not cleaned:
        raise ValueError("Mã Mermaid không chứa cú pháp hợp lệ.")

    # 3. Tìm dòng lệnh đầu tiên không phải comment (%%) và không rỗng để xác định từ khóa
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

    # Xác định kiểu sơ đồ hiệu dụng
    norm_type = diagram_type.strip().lower() if diagram_type else ""
    is_erd = (norm_type in ("erdiagram", "erd")) or (matched_keyword == "erDiagram")
    is_seq = (norm_type in ("sequencediagram", "sequence")) or (matched_keyword == "sequenceDiagram")

    # 4. Áp dụng quy tắc làm sạch theo từng loại sơ đồ
    processed_lines: List[str] = []

    if is_erd:
        in_entity_block = False
        for line in lines:
            stripped = line.strip()
            if "{" in stripped and "}" in stripped:
                # Khối thực thể trên cùng 1 dòng
                prefix, rest = line.split("{", 1)
                body, suffix = rest.rsplit("}", 1)
                cleaned_body = re.sub(r'([a-zA-Z0-9_]+)\s*\([^)]*\)', r'\1', body)
                cleaned_body = re.sub(r',\s*$', '', cleaned_body.strip()).replace(',', ' ')
                tokens = cleaned_body.split()
                processed_lines.append(f"{prefix}{{ {' '.join(tokens)} }}{suffix}")
            elif "{" in stripped:
                in_entity_block = True
                processed_lines.append(line)
            elif "}" in stripped:
                in_entity_block = False
                processed_lines.append(line)
            elif in_entity_block:
                processed_lines.append(_clean_erd_attribute_line(line))
            else:
                processed_lines.append(line)
    elif is_seq:
        for line in lines:
            cleaned_line = _clean_seq_participant_line(line)
            cleaned_line = _clean_seq_message_line(cleaned_line)
            processed_lines.append(cleaned_line)
    else:
        processed_lines = lines

    return "\n".join(processed_lines)


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
