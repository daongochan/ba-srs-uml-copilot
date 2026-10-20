"""Unit tests for Mermaid and SQL DDL syntax validators."""

import pytest
from src.validators.syntax_validator import (
    clean_and_validate_mermaid,
    validate_sql_ddl,
)


class TestMermaidValidator:
    """Test suite for clean_and_validate_mermaid function."""

    def test_clean_sequence_diagram_with_markdown_fence(self):
        raw_code = """```mermaid
sequenceDiagram
    autonumber
    actor User as Khách hàng
    participant Web as Giao diện Web
    participant Server as Backend API
    User->>Web: Chọn ghế ngồi
    Web->>Server: Gửi yêu cầu giữ chỗ tạm thời (10 phút)
    Server-->>Web: Trả về trạng thái khóa ghế thành công
```"""
        cleaned = clean_and_validate_mermaid(raw_code)
        assert cleaned.startswith("sequenceDiagram")
        assert not cleaned.startswith("```")
        assert not cleaned.endswith("```")
        assert "User->>Web: Chọn ghế ngồi" in cleaned

    def test_clean_er_diagram_with_generic_code_fence(self):
        raw_code = """```
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : included_in
```"""
        cleaned = clean_and_validate_mermaid(raw_code)
        assert cleaned.startswith("erDiagram")
        assert "CUSTOMER ||--o{ ORDER : places" in cleaned

    def test_mermaid_already_clean(self):
        raw_code = """sequenceDiagram
    Customer->>Bank: Transfer money
    Bank-->>Customer: Confirmation"""
        cleaned = clean_and_validate_mermaid(raw_code)
        assert cleaned == raw_code.strip()

    def test_mermaid_with_leading_comments(self):
        raw_code = """%% This is a header comment
%% Another author comment
sequenceDiagram
    Alice->>Bob: Hello"""
        cleaned = clean_and_validate_mermaid(raw_code)
        assert "sequenceDiagram" in cleaned
        assert "Alice->>Bob: Hello" in cleaned

    def test_mermaid_case_insensitive_keyword(self):
        raw_code = """sequencediagram
    Alice->>Bob: Hello"""
        cleaned = clean_and_validate_mermaid(raw_code)
        assert "sequencediagram" in cleaned

    def test_invalid_mermaid_keyword(self):
        raw_code = """```mermaid
flowchart TD
    A[Start] --> B[End]
```"""
        with pytest.raises(ValueError) as exc_info:
            clean_and_validate_mermaid(raw_code)
        assert "phải là 'sequenceDiagram' hoặc 'erDiagram'" in str(exc_info.value)

    def test_empty_mermaid_raises_error(self):
        with pytest.raises(ValueError) as exc_info:
            clean_and_validate_mermaid("   ")
        assert "không được để trống" in str(exc_info.value)

    def test_no_valid_syntax_raises_error(self):
        with pytest.raises(ValueError):
            clean_and_validate_mermaid("%% only comments\n%% line 2")


class TestSqlDdlValidator:
    """Test suite for validate_sql_ddl function."""

    def test_valid_single_create_table_with_markdown(self):
        sql = """```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```"""
        is_valid, message = validate_sql_ddl(sql)
        assert is_valid is True
        assert "hợp lệ" in message

    def test_valid_multiple_create_tables_and_foreign_keys(self):
        sql = """
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    salary NUMERIC(10, 2) NOT NULL,
    dept_id INT NOT NULL REFERENCES departments(dept_id)
);
"""
        is_valid, message = validate_sql_ddl(sql)
        assert is_valid is True
        assert "hợp lệ" in message

    def test_empty_sql_script(self):
        is_valid, message = validate_sql_ddl("   ")
        assert is_valid is False
        assert "trống" in message

    def test_sql_with_syntax_error(self):
        # Thiếu dấu đóng ngoặc hoặc kiểu dữ liệu không hợp lệ
        invalid_sql = "CREATE TABLE broken_table (id INT PRIMARY KEY, name VARCHAR("
        is_valid, message = validate_sql_ddl(invalid_sql)
        assert is_valid is False
        assert "Lỗi cú pháp SQL" in message

    def test_sql_without_create_table(self):
        query_sql = "SELECT * FROM users WHERE active = true;"
        is_valid, message = validate_sql_ddl(query_sql)
        assert is_valid is False
        assert "Không tìm thấy câu lệnh 'CREATE TABLE'" in message
