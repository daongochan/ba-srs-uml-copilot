"""Unit tests for Mermaid and SQL DDL syntax validators."""

import pytest
from src.validators.syntax_validator import (
    clean_and_validate_mermaid,
    validate_sql_ddl,
)
from src.validators.db_sandbox import execute_and_audit_ddl
from src.validators.requirements_linter import evaluate_srs_deterministically
from src.models.srs_schema import (
    AcceptanceCriterion,
    FunctionalRequirement,
    NonFunctionalRequirement,
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

    def test_execute_and_audit_ddl_detects_unindexed_foreign_key(self):
        """Test case 1: Phát hiện FK chưa đánh index và tự động sinh câu lệnh CREATE INDEX khắc phục."""
        sql = """
CREATE TABLE parent (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE child (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES parent(id),
    name VARCHAR(100) NOT NULL
);
"""
        result = execute_and_audit_ddl(sql)
        assert result["execution_success"] is True
        assert result["table_count"] == 2
        assert result["total_foreign_keys"] == 1
        assert len(result["unindexed_foreign_keys"]) == 1
        assert result["unindexed_foreign_keys"][0]["table"] == "child"
        assert result["unindexed_foreign_keys"][0]["fk_column"] == "parent_id"
        assert result["unindexed_foreign_keys"][0]["referenced_table"] == "parent"
        assert "CREATE INDEX IF NOT EXISTS idx_child_parent_id ON child (parent_id);" in result["recommended_index_script"]
        assert result["performance_health_score"] == 90
        assert result["total_indexes_created"] == 0

    def test_execute_and_audit_ddl_indexed_foreign_key_has_perfect_score(self):
        """Test case 2: Bảng có FK đã được đánh B-Tree index đạt điểm 100/100."""
        sql = """
CREATE TABLE parent (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE child (
    id SERIAL PRIMARY KEY,
    parent_id INT NOT NULL REFERENCES parent(id),
    name VARCHAR(100) NOT NULL
);

CREATE INDEX idx_child_parent_id ON child (parent_id);
"""
        result = execute_and_audit_ddl(sql)
        assert result["execution_success"] is True
        assert result["table_count"] == 2
        assert result["total_foreign_keys"] == 1
        assert len(result["unindexed_foreign_keys"]) == 0
        assert result["recommended_index_script"] == ""
        assert result["performance_health_score"] == 100
        assert result["total_indexes_created"] == 1



class TestRequirementsLinter:
    """Test suite for deterministic IEEE 29148 and INVEST requirements linter."""

    def test_evaluate_srs_deterministically_perfect_document(self):
        """Xác nhận tài liệu SRS chuẩn mực đạt 100 điểm IEEE, 100 điểm INVEST và 100% độ phủ RTM."""
        doc = SRSDocument(
            project_title="CineMax Online Booking System",
            business_objective="Xây dựng nền tảng đặt vé trực tuyến giúp tăng 30% doanh thu và loại bỏ trùng ghế.",
            actors=["Khách hàng", "Quản trị viên"],
            functional_requirements=[
                FunctionalRequirement(
                    req_id="FR-01",
                    title="Đặt vé xem phim trực tuyến",
                    user_story="Là một khách hàng, tôi muốn đặt vé xem phim trực tuyến để tiết kiệm thời gian chờ đợi tại quầy.",
                    priority="High",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            given="Khách hàng đã đăng nhập và đang xem lịch chiếu phim còn ghế trống",
                            when="Khách hàng chọn ghế A1 và bấm nút xác nhận thanh toán",
                            then="Hệ thống tạo mã đơn hàng duy nhất và giữ chỗ thành công trong 10 phút.",
                        )
                    ],
                ),
                FunctionalRequirement(
                    req_id="FR-02",
                    title="Quản lý suất chiếu",
                    user_story="As an administrator, I want to create new movie showtimes so that customers can book tickets.",
                    priority="Medium",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            given="Quản trị viên đã đăng nhập trang quản trị rạp chiếu phim",
                            when="Quản trị viên nhập thông tin phòng chiếu và thời gian bắt đầu",
                            then="Hệ thống lưu suất chiếu mới vào cơ sở dữ liệu và hiển thị lên lịch chiếu.",
                        )
                    ],
                ),
            ],
            non_functional_requirements=[
                NonFunctionalRequirement(
                    category="Performance",
                    description="Thời gian phản hồi API tra cứu trạng thái ghế",
                    metric="Thời gian phản hồi trung bình < 250ms cho 99% các yêu cầu đồng thời.",
                ),
                NonFunctionalRequirement(
                    category="Scalability",
                    description="Khả năng chịu tải đồng thời trong giờ cao điểm",
                    metric="Đáp ứng tối thiểu 3000 người dùng truy cập và đặt chỗ đồng thời.",
                ),
            ],
            sequence_diagram_mermaid="""sequenceDiagram
    actor U as "Khách hàng"
    participant S as "Hệ thống"
    U->>S: Đặt vé
    S-->>U: Xác nhận""",
            er_diagram_mermaid="""erDiagram
    BOOKINGS {
        int id PK
        varchar code
    }""",
            sql_ddl_script="CREATE TABLE bookings (id INT PRIMARY KEY, code VARCHAR(50));",
            traceability_matrix=[
                TraceabilityItem(
                    req_id="FR-01",
                    feature_name="Đặt vé xem phim",
                    business_rule="Ghế phải ở trạng thái trống trước khi khóa ghế tạm thời",
                    related_tables=["bookings"],
                    test_scenario_summary="Kiểm thử luồng giữ chỗ thành công khi chọn ghế còn trống",
                ),
                TraceabilityItem(
                    req_id="FR-02",
                    feature_name="Quản lý suất chiếu",
                    business_rule="Phòng chiếu không được trùng lịch chiếu cùng khung giờ",
                    related_tables=["showtimes"],
                    test_scenario_summary="Kiểm thử tạo suất chiếu mới và kiểm tra xung đột phòng chiếu",
                ),
            ],
            quality_audit=QualityAudit(ieee_compliance_score=95, invest_score=90),
        )

        result = evaluate_srs_deterministically(doc)

        assert result["deterministic_ieee_score"] == 100
        assert result["deterministic_invest_score"] == 100
        assert result["rtm_coverage_pct"] == 100.0
        assert len(result["lint_warnings"]) == 0
        assert result["stats"]["weasel_count"] == 0
        assert result["stats"]["unquantified_nfr_count"] == 0

    def test_evaluate_srs_deterministically_with_weasel_words_and_unquantified_nfr(self):
        """Xác nhận điểm bị trừ chính xác và lint_warnings bắt đúng lỗi khi có từ ngữ mơ hồ 'nhanh chóng' và NFR thiếu số liệu."""
        doc = SRSDocument(
            project_title="CineMax Online Booking System",
            business_objective="Xây dựng nền tảng đặt vé trực tuyến.",
            actors=["Khách hàng"],
            functional_requirements=[
                FunctionalRequirement(
                    req_id="FR-01",
                    title="Đặt vé xem phim trực tuyến",
                    user_story="Là một khách hàng, tôi muốn đặt vé nhanh chóng để tiết kiệm thời gian chờ đợi.",
                    priority="High",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            given="Khách hàng đã đăng nhập và đang xem lịch chiếu phim còn ghế",
                            when="Khách hàng chọn ghế A1 và xác nhận thanh toán",
                            then="Hệ thống tạo mã đơn hàng duy nhất và giữ chỗ thành công trong 10 phút.",
                        )
                    ],
                )
            ],
            non_functional_requirements=[
                NonFunctionalRequirement(
                    category="Performance",
                    description="Hệ thống phải hoạt động mượt mà và ổn định",
                    metric="Phản hồi mượt mà không bị gián đoạn",  # Thiếu số liệu định lượng (không có \d+)
                )
            ],
            sequence_diagram_mermaid="""sequenceDiagram
    actor U as "Khách hàng"
    participant S as "Hệ thống"
    U->>S: Đặt vé
    S-->>U: Xác nhận""",
            er_diagram_mermaid="""erDiagram
    BOOKINGS {
        int id PK
    }""",
            sql_ddl_script="CREATE TABLE bookings (id INT PRIMARY KEY);",
            traceability_matrix=[
                TraceabilityItem(
                    req_id="FR-01",
                    feature_name="Đặt vé xem phim",
                    business_rule="Ghế phải ở trạng thái trống",
                    related_tables=["bookings"],
                    test_scenario_summary="Kiểm thử giữ chỗ thành công",
                )
            ],
        )

        result = evaluate_srs_deterministically(doc)

        # 1 weasel word (-5 IEEE, -5 INVEST)
        # 1 unquantified NFR (-10 IEEE, 0 INVEST)
        # RTM coverage = 100.0% (0 deduction)
        assert result["deterministic_ieee_score"] == 85  # 100 - 5 - 10 = 85
        assert result["deterministic_invest_score"] == 95  # 100 - 5 = 95
        assert result["rtm_coverage_pct"] == 100.0

        # Kiểm tra lint_warnings bắt đúng 2 cảnh báo cụ thể
        assert len(result["lint_warnings"]) == 2
        assert any("nhanh chóng" in w for w in result["lint_warnings"])
        assert any("FR-01" in w for w in result["lint_warnings"])
        assert any("định lượng" in w or "Performance" in w for w in result["lint_warnings"])
        assert result["stats"]["weasel_count"] == 1
        assert result["stats"]["unquantified_nfr_count"] == 1

    def test_evaluate_srs_deterministically_invalid_story_format_and_short_then(self):
        """Kiểm tra phát hiện lỗi cú pháp User Story và mệnh đề Then quá ngắn (< 15 ký tự)."""
        doc = SRSDocument(
            project_title="Test App",
            business_objective="Kiểm tra phát hiện lỗi cú pháp.",
            actors=["Người dùng"],
            functional_requirements=[
                FunctionalRequirement(
                    req_id="FR-01",
                    title="Chức năng không chuẩn",
                    user_story="Người dùng muốn hủy đơn hàng trực tiếp.",  # Không đúng cấu trúc Là một... tôi muốn... để...
                    priority="Medium",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            given="Đơn hàng đang chờ xử lý",
                            when="Bấm nút hủy",
                            then="Đã hủy đơn.",  # Quá ngắn: 12 ký tự < 15 ký tự tối thiểu
                        )
                    ],
                )
            ],
            non_functional_requirements=[
                NonFunctionalRequirement(
                    category="Security",
                    description="Mã hóa mật khẩu bằng bcrypt",
                    metric="100% mật khẩu được băm an toàn.",
                )
            ],
            sequence_diagram_mermaid="sequenceDiagram\n    actor U as \"U\"\n    U->>S: req",
            er_diagram_mermaid="erDiagram\n    T { int id PK }",
            sql_ddl_script="CREATE TABLE t (id INT PRIMARY KEY);",
            traceability_matrix=[
                TraceabilityItem(
                    req_id="FR-01",
                    feature_name="Hủy đơn",
                    business_rule="Chỉ hủy khi đơn chưa xuất kho",
                    related_tables=["t"],
                    test_scenario_summary="Kiểm thử hủy đơn hàng",
                )
            ],
        )

        result = evaluate_srs_deterministically(doc)

        assert any("cấu trúc chuẩn" in w for w in result["lint_warnings"])
        assert any("Then" in w and "quá ngắn" in w for w in result["lint_warnings"])
        assert result["deterministic_invest_score"] < 90

    def test_evaluate_srs_deterministically_missing_rtm_coverage(self):
        """Kiểm tra phát hiện thiếu ánh xạ trong Ma trận Truy vết RTM."""
        doc = SRSDocument(
            project_title="Test RTM Coverage",
            business_objective="Kiểm tra RTM coverage.",
            actors=["Khách hàng"],
            functional_requirements=[
                FunctionalRequirement(
                    req_id="FR-01",
                    title="Tính năng 1",
                    user_story="Là một khách hàng, tôi muốn thanh toán trực tuyến để nhận vé ngay lập tức.",
                    priority="High",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            given="Đã chọn ghế và chuyển sang cổng thanh toán",
                            when="Thanh toán thành công",
                            then="Hệ thống xác nhận giao dịch thành công và gửi vé qua email.",
                        )
                    ],
                ),
                FunctionalRequirement(
                    req_id="FR-02",
                    title="Tính năng 2",
                    user_story="Là một khách hàng, tôi muốn hủy vé xem phim để nhận lại tiền hoàn vé.",
                    priority="Low",
                    acceptance_criteria=[
                        AcceptanceCriterion(
                            given="Vé chưa đến giờ chiếu tối thiểu 2 tiếng",
                            when="Bấm yêu cầu hoàn vé",
                            then="Hệ thống hủy vé và hoàn tiền theo chính sách hoàn trả rạp.",
                        )
                    ],
                ),
            ],
            non_functional_requirements=[
                NonFunctionalRequirement(
                    category="Availability",
                    description="Độ sẵn sàng của hệ thống",
                    metric="Uptime đạt 99.9% hàng tháng.",
                )
            ],
            sequence_diagram_mermaid="sequenceDiagram\n    actor U as \"U\"\n    U->>S: req",
            er_diagram_mermaid="erDiagram\n    T { int id PK }",
            sql_ddl_script="CREATE TABLE t (id INT PRIMARY KEY);",
            traceability_matrix=[
                # Chỉ có FR-01, thiếu FR-02 -> Coverage = 50.0%
                TraceabilityItem(
                    req_id="FR-01",
                    feature_name="Thanh toán trực tuyến",
                    business_rule="Xác thực thanh toán qua cổng",
                    related_tables=["t"],
                    test_scenario_summary="Kiểm thử thanh toán",
                )
            ],
        )

        result = evaluate_srs_deterministically(doc)

        assert result["rtm_coverage_pct"] == 50.0
        assert any("FR-02" in w and "Ma trận Truy vết" in w for w in result["lint_warnings"])
        assert result["deterministic_ieee_score"] < 100

    def test_evaluate_srs_deterministically_none_raises_error(self):
        """Xác nhận evaluate_srs_deterministically raise ValueError nếu doc là None."""
        with pytest.raises(ValueError, match="không được để trống"):
            evaluate_srs_deterministically(None)


