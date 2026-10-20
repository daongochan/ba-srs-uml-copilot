"""Unit tests for Mermaid and SQL DDL syntax validators."""

import pytest
from src.validators.syntax_validator import (
    clean_and_validate_mermaid,
    validate_sql_ddl,
)
from src.validators.db_sandbox import execute_and_audit_ddl
from src.models.srs_schema import (
    TraceabilityItem,
    QualityAudit,
    SRSDocument,
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

    def test_clean_er_diagram_removes_data_type_sizes_and_commas(self):
        raw_code = """```mermaid
erDiagram
    CUSTOMER {
        int(11) id PK,
        varchar(150) username "Tên đăng nhập",
        varchar(255) email,
        decimal(10, 2) balance,
        timestamp created_at,
    }
    TICKET {
        int ticket_id PK,
        int customer_id FK,
        numeric(12, 4) price "Giá vé (VNĐ)",
    }
    CUSTOMER ||--o{ TICKET : owns
```"""
        cleaned = clean_and_validate_mermaid(raw_code, diagram_type="erDiagram")
        # Kiểm tra không còn kích thước trong ngoặc đơn ở kiểu dữ liệu
        assert "varchar(150)" not in cleaned
        assert "decimal(10, 2)" not in cleaned
        assert "int(11)" not in cleaned
        assert "numeric(12, 4)" not in cleaned
        # Kiểm tra kiểu dữ liệu đã được làm sạch
        assert "int id PK" in cleaned
        assert 'varchar username "Tên đăng nhập"' in cleaned
        assert "varchar email" in cleaned
        assert "decimal balance" in cleaned
        assert "timestamp created_at" in cleaned
        assert 'numeric price "Giá vé (VNĐ)"' in cleaned
        # Đảm bảo không còn dấu phẩy ở cuối dòng thuộc tính
        for line in cleaned.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("erDiagram") and not stripped.endswith("{") and not stripped.endswith("}"):
                if "PK" in stripped or "FK" in stripped or "varchar" in stripped:
                    assert not stripped.endswith(","), f"Dòng vẫn còn dấu phẩy: {stripped}"

    def test_clean_mermaid_escaped_newlines(self):
        raw_code = "sequenceDiagram\\nautonumber\\nactor User as Khách hàng\\nUser->>Web: Chọn ghế ngồi"
        cleaned = clean_and_validate_mermaid(raw_code)
        assert "\n" in cleaned
        assert "\\n" not in cleaned
        assert cleaned.startswith("sequenceDiagram")
        assert 'actor User as "Khách hàng"' in cleaned

    def test_clean_sequence_diagram_participant_quoting(self):
        raw_code = """sequenceDiagram
    actor Khách hàng
    participant Web as Giao diện Web
    participant Server as Backend API
    actor User as "Người Dùng"
    participant DB
    User->>Web: Đăng nhập;
    Web->>Server: Gửi {username, password};
    Server->>DB: Truy vấn dữ liệu;
"""
        cleaned = clean_and_validate_mermaid(raw_code, diagram_type="sequenceDiagram")
        # Kiểm tra format ID as "Display Name"
        assert 'actor Khach_hang as "Khách hàng"' in cleaned
        assert 'participant Web as "Giao diện Web"' in cleaned
        assert 'participant Server as "Backend API"' in cleaned
        assert 'actor User as "Người Dùng"' in cleaned
        assert "participant DB" in cleaned
        # Kiểm tra nội dung message đã loại bỏ ';' và '{}'
        assert "User->>Web: Đăng nhập" in cleaned
        assert "Web->>Server: Gửi (username, password)" in cleaned
        assert "Server->>DB: Truy vấn dữ liệu" in cleaned

    def test_clean_state_diagram_v2_and_sanitization(self):
        raw_code = """```mermaid
stateDiagram
    [*] --> Pending : Tạo đơn hàng;
    Pending --> Paid : Thanh toán thành công;
    Pending --> Cancelled : Hết hạn giữ chỗ (10 phút);
    Paid --> [*] : Hoàn tất đơn hàng;
```"""
        cleaned = clean_and_validate_mermaid(raw_code, diagram_type="stateDiagram-v2")
        assert cleaned.startswith("stateDiagram-v2")
        assert "```" not in cleaned
        assert "Pending --> Paid : Thanh toán thành công" in cleaned
        assert "Pending --> Cancelled : Hết hạn giữ chỗ (10 phút)" in cleaned
        for line in cleaned.splitlines():
            stripped = line.strip()
            if ":" in stripped and "-->" in stripped:
                assert not stripped.endswith(";"), f"Dòng vẫn còn dấu chấm phẩy: {stripped}"

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


class TestRtmAndQualityAuditSchemas:
    """Test suite for TraceabilityItem and QualityAudit models."""

    def test_traceability_item_creation(self):
        item = TraceabilityItem(
            req_id="FR-01",
            feature_name="Khóa ghế tạm thời",
            business_rule="Ghế được khóa trong 10 phút, tự giải phóng nếu chưa thanh toán",
            related_tables=["tickets", "seats", "bookings"],
            test_scenario_summary="Kiểm thử chọn ghế, đợi 10 phút và xác minh trạng thái ghế tự đổi về trống",
        )
        assert item.req_id == "FR-01"
        assert item.feature_name == "Khóa ghế tạm thời"
        assert len(item.related_tables) == 3
        assert "tickets" in item.related_tables

    def test_quality_audit_creation(self):
        audit = QualityAudit(
            ieee_compliance_score=95,
            invest_score=92,
            third_nf_justification="Bảng tickets tách riêng customer_id để loại bỏ phụ thuộc từng phần 2NF...",
            clarification_questions=[
                "Chính sách hoàn tiền khi hủy vé trước giờ chiếu bao lâu?",
                "Có giới hạn số lượng vé đặt tối đa cho một tài khoản không?",
            ],
        )
        assert audit.ieee_compliance_score == 95
        assert audit.invest_score == 92
        assert len(audit.clarification_questions) == 2
        assert "hoàn tiền" in audit.clarification_questions[0]

    def test_srs_document_with_rtm_and_quality_audit(self):
        item = TraceabilityItem(
            req_id="FR-01",
            feature_name="Đặt vé trực tuyến",
            business_rule="Phải thanh toán thành công trong 10 phút",
            related_tables=["bookings", "payments"],
            test_scenario_summary="Xác nhận tạo đơn đặt vé và chuyển hướng sang cổng thanh toán",
        )
        audit = QualityAudit(
            ieee_compliance_score=98,
            invest_score=95,
            third_nf_justification="Đã chuẩn hóa 3NF hoàn chỉnh, triệt tiêu phụ thuộc bắc cầu.",
            clarification_questions=["Cần xác nhận cổng thanh toán MoMo/VNPAY"],
        )
        doc = SRSDocument(
            project_title="CineMax System",
            business_objective="Tối ưu đặt vé",
            sequence_diagram_mermaid="sequenceDiagram\n  User->>Web: Dat ve",
            er_diagram_mermaid="erDiagram\n  CUSTOMER ||--o{ BOOKING : places",
            sql_ddl_script="CREATE TABLE bookings (id INT PRIMARY KEY);",
            traceability_matrix=[item],
            quality_audit=audit,
        )
        assert len(doc.traceability_matrix) == 1
        assert doc.traceability_matrix[0].req_id == "FR-01"
        assert doc.quality_audit is not None
        assert doc.quality_audit.ieee_compliance_score == 98
        assert "MoMo" in doc.quality_audit.clarification_questions[0]


class TestDbSandbox:
    """Test suite for in-memory SQLite DDL execution sandbox."""

    def test_execute_and_audit_ddl_two_tables_with_foreign_key(self):
        sql = """```sql
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dept_id INT REFERENCES departments(dept_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```"""
        result = execute_and_audit_ddl(sql)
        assert result["execution_success"] is True
        assert result["table_count"] == 2
        assert result["total_foreign_keys"] == 1
        assert result["error_message"] is None
        assert len(result["tables_metadata"]) == 2

        dept_meta = next(t for t in result["tables_metadata"] if t["table_name"] == "departments")
        assert dept_meta["column_count"] == 2
        assert dept_meta["foreign_key_count"] == 0

        emp_meta = next(t for t in result["tables_metadata"] if t["table_name"] == "employees")
        assert emp_meta["column_count"] == 4
        assert emp_meta["foreign_key_count"] == 1
        assert emp_meta["referenced_tables"] == ["departments"]

    def test_execute_and_audit_ddl_with_postgres_uuid_default(self):
        sql = """
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE
);
"""
        result = execute_and_audit_ddl(sql)
        assert result["execution_success"] is True
        assert result["table_count"] == 1
        assert result["total_foreign_keys"] == 0

    def test_execute_and_audit_ddl_empty(self):
        result = execute_and_audit_ddl("   ")
        assert result["execution_success"] is False
        assert result["table_count"] == 0
        assert "trống" in result["error_message"].lower()

    def test_execute_and_audit_ddl_syntax_error(self):
        result = execute_and_audit_ddl("CREATE TABLE broken (id INT PRIMARY KEY, name VARCHAR(")
        assert result["execution_success"] is False
        assert result["error_message"] is not None

    def test_execute_and_audit_ddl_with_postgres_index_nulls_last(self):
        """Verify executing SQL containing Postgres-specific NULLS LAST and USING BTREE indexes succeeds."""
        sql = """
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL
);

CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_created ON bookings (created_at DESC NULLS LAST);
CREATE INDEX CONCURRENTLY idx_bookings_customer ON bookings USING BTREE (customer_id);
"""
        result = execute_and_audit_ddl(sql)
        assert result["execution_success"] is True
        assert result["table_count"] == 2
        assert result["total_foreign_keys"] == 1
        assert result["error_message"] is None
        assert len(result["tables_metadata"]) == 2

