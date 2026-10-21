"""Unit tests for SRS Markdown export functionality."""

from src.models.srs_schema import (
    AcceptanceCriterion,
    FunctionalRequirement,
    NonFunctionalRequirement,
    SRSDocument,
)
from src.app import export_srs_markdown


def test_export_srs_markdown_contains_all_sections():
    ac = AcceptanceCriterion(
        given="Khách hàng ở trang đăng ký",
        when="Nhập email hợp lệ",
        then="Hệ thống gửi mã OTP",
    )
    fr = FunctionalRequirement(
        req_id="FR-01",
        title="Đăng ký tài khoản",
        user_story="Là khách hàng, tôi muốn đăng ký tài khoản...",
        priority="High",
        acceptance_criteria=[ac],
    )
    nfr = NonFunctionalRequirement(
        category="Security",
        description="Mã hóa mật khẩu theo chuẩn bcrypt",
        metric="Cost factor >= 12",
    )
    doc = SRSDocument(
        project_title="Cửa Hàng Trực Tuyến",
        business_objective="Tăng trưởng doanh số bán lẻ trực tuyến.",
        actors=["Khách hàng", "Quản trị viên"],
        functional_requirements=[fr],
        non_functional_requirements=[nfr],
        sequence_diagram_mermaid="sequenceDiagram\n  autonumber\n  User->>Server: Register",
        er_diagram_mermaid="erDiagram\n  USERS ||--o{ ORDERS : places",
        sql_ddl_script="CREATE TABLE users (id SERIAL PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE);",
    )

    md = export_srs_markdown(doc)

    assert "# Cửa Hàng Trực Tuyến" in md
    assert "## 1. Mục tiêu Kinh doanh & Phạm vi Hệ thống" in md
    assert "Tăng trưởng doanh số bán lẻ trực tuyến." in md
    assert "## 2. Danh sách Tác nhân Tham gia (Actors)" in md
    assert "**Khách hàng**" in md
    assert "**Quản trị viên**" in md
    assert "## 3. Đặc tả Yêu cầu Chức năng (Functional Requirements)" in md
    assert "FR-01: Đăng ký tài khoản" in md
    assert "Gherkin BDD" in md
    assert "## 4. Đặc tả Yêu cầu Phi Chức năng (Non-Functional Requirements)" in md
    assert "Cost factor >= 12" in md
    assert "## 5. Sơ đồ Tuần tự Nghiệp vụ Trọng tâm (UML Sequence Diagram)" in md
    assert "sequenceDiagram" in md
    assert "## 6. Sơ đồ Thực thể Quan hệ Chuẩn 3NF (Mermaid ERD)" in md
    assert "erDiagram" in md
    assert "## 7. Kịch bản Khởi tạo Cơ sở Dữ liệu (SQL DDL Script - PostgreSQL)" in md
    assert "CREATE TABLE users" in md


def test_export_srs_markdown_backward_compatible_without_state_machine():
    """Verify export_srs_markdown gracefully handles legacy documents missing new fields."""

    class LegacySRSDocument:
        project_title = "Legacy System"
        business_objective = "Legacy Objective"
        actors = ["Admin"]
        functional_requirements = []
        non_functional_requirements = []
        sequence_diagram_mermaid = "sequenceDiagram\n  A->>B: Ping"
        er_diagram_mermaid = "erDiagram\n  A ||--o{ B : rel"
        sql_ddl_script = "CREATE TABLE a (id INT);"
        # Deliberately missing: state_diagram_mermaid, state_machine_entity, traceability_matrix, quality_audit

    legacy_doc = LegacySRSDocument()
    # Must not raise AttributeError
    md = export_srs_markdown(legacy_doc)  # type: ignore[arg-type]
    assert "# Legacy System" in md
    assert "5.1. Sơ đồ Máy Trạng thái" not in md
