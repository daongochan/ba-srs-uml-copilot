"""Unit tests for exporter service: Markdown report, RTM CSV, and ZIP Bundle."""

import io
import zipfile
import pytest

from src.models.srs_schema import (
    AcceptanceCriterion,
    FunctionalRequirement,
    NonFunctionalRequirement,
    QualityAudit,
    SRSDocument,
    TraceabilityItem,
)
from src.services.exporter import (
    create_project_bundle_zip,
    generate_markdown_report,
    generate_rtm_csv_bytes,
)


@pytest.fixture
def sample_srs_doc() -> SRSDocument:
    ac = AcceptanceCriterion(
        given="Khách hàng chọn ghế A1",
        when="Bấm nút Giữ chỗ",
        then="Hệ thống chuyển trạng thái ghế sang Locked trong 10 phút",
    )
    fr = FunctionalRequirement(
        req_id="FR-01",
        title="Khóa ghế tạm thời",
        user_story="Là khách hàng, tôi muốn giữ chỗ để thanh toán không bị tranh vé.",
        priority="Must Have",
        acceptance_criteria=[ac],
    )
    nfr = NonFunctionalRequirement(
        category="Performance",
        description="Thời gian phản hồi khi khóa ghế",
        metric="Response Time < 200ms",
    )
    rtm = TraceabilityItem(
        req_id="FR-01",
        feature_name="Khóa ghế tạm thời",
        business_rule="Mỗi ghế chỉ được giữ tối đa 10 phút trước khi tự động hủy",
        related_tables=["seats", "seat_locks"],
        test_scenario_summary="Xác nhận ghế chuyển sang Locked và nhả sau 10 phút nếu chưa thanh toán",
    )
    qa = QualityAudit(
        ieee_compliance_score=95,
        invest_score=92,
        third_nf_justification="Tách bảng seats và seat_locks để loại bỏ phụ thuộc bắc cầu.",
        clarification_questions=["Cần xác nhận cổng thanh toán mặc định là VNPay hay MoMo?"],
    )
    return SRSDocument(
        project_title="CineMax Cinema Management",
        business_objective="Tối ưu hóa doanh thu và trải nghiệm đặt vé của khách hàng.",
        actors=["Khách hàng", "Thu ngân"],
        functional_requirements=[fr],
        non_functional_requirements=[nfr],
        sequence_diagram_mermaid="sequenceDiagram\n  autonumber\n  Customer->>Server: Lock Seat",
        state_machine_entity="Vòng đời Trạng thái Ghế ngồi (Seat Lifecycle)",
        state_diagram_mermaid="stateDiagram-v2\n  [*] --> Available\n  Available --> Locked: Lock\n  Locked --> [*]",
        er_diagram_mermaid="erDiagram\n  SEATS ||--o{ SEAT_LOCKS : has",
        sql_ddl_script="CREATE TABLE seats (id SERIAL PRIMARY KEY, code VARCHAR NOT NULL);",
        traceability_matrix=[rtm],
        quality_audit=qa,
    )


def test_generate_markdown_report(sample_srs_doc: SRSDocument):
    md = generate_markdown_report(sample_srs_doc)

    assert "# CineMax Cinema Management" in md
    assert "## 1. Mục tiêu Kinh doanh & Phạm vi Hệ thống" in md
    assert "## 2. Danh sách Tác nhân Tham gia (Actors)" in md
    assert "**Khách hàng**" in md
    assert "## 3. Đặc tả Yêu cầu Chức năng (Functional Requirements)" in md
    assert "FR-01: Khóa ghế tạm thời" in md
    assert "## 4. Đặc tả Yêu cầu Phi Chức năng (Non-Functional Requirements)" in md
    assert "Response Time < 200ms" in md
    assert "## 5. Sơ đồ Tuần tự Nghiệp vụ Trọng tâm (UML Sequence Diagram)" in md
    assert "Customer->>Server: Lock Seat" in md
    assert "## 5.1. Sơ đồ Máy Trạng thái Thực thể Cốt lõi" in md
    assert "Seat Lifecycle" in md
    assert "## 6. Sơ đồ Thực thể Quan hệ Chuẩn 3NF (Mermaid ERD)" in md
    assert "SEATS ||--o{ SEAT_LOCKS" in md
    assert "## 7. Kịch bản Khởi tạo Cơ sở Dữ liệu (SQL DDL Script - PostgreSQL)" in md
    assert "CREATE TABLE seats" in md
    assert "## 8. Ma trận Truy vết Yêu cầu (Requirements Traceability Matrix - RTM)" in md
    assert "seat_locks" in md
    assert "## 9. Đánh giá Chất lượng Đặc tả & Điểm Cần Phỏng vấn Lại (Quality & Ambiguity Audit)" in md
    assert "VNPay hay MoMo" in md


def test_generate_rtm_csv_bytes(sample_srs_doc: SRSDocument):
    csv_bytes = generate_rtm_csv_bytes(sample_srs_doc)

    # 1. Bắt buộc bắt đầu bằng UTF-8 BOM để Excel hiển thị tiếng Việt không lỗi font
    assert csv_bytes.startswith(b"\xef\xbb\xbf")

    # 2. Giải mã và kiểm tra nội dung
    csv_text = csv_bytes.decode("utf-8-sig")
    assert "Mã YC" in csv_text
    assert "Tên Tính năng" in csv_text
    assert "Quy tắc Nghiệp vụ" in csv_text
    assert "Bảng CSDL Liên quan" in csv_text
    assert "Kịch bản Kiểm thử Nghiệm thu" in csv_text
    assert "FR-01" in csv_text
    assert "Khóa ghế tạm thời" in csv_text
    assert "seats, seat_locks" in csv_text


def test_create_project_bundle_zip(sample_srs_doc: SRSDocument):
    md = generate_markdown_report(sample_srs_doc)
    zip_bytes = create_project_bundle_zip(sample_srs_doc, md)

    # Kiểm tra tính hợp lệ của file ZIP bằng zipfile.ZipFile
    zip_buffer = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_buffer, mode="r") as zf:
        file_list = zf.namelist()

        # Xác nhận đủ đúng 7 file thành phần theo chuẩn Enterprise Export Bundle
        expected_files = [
            "01_SRS_Specification_IEEE29148.md",
            "02_Database_Schema_3NF.sql",
            "03_Traceability_Matrix_RTM.csv",
            "04_System_Architecture_Model.json",
            "diagrams/sequence_diagram.mmd",
            "diagrams/state_machine.mmd",
            "diagrams/erd_3nf.mmd",
        ]
        for expected in expected_files:
            assert expected in file_list, f"Thiếu file {expected} trong ZIP bundle!"

        # Đọc kiểm tra nội dung một số tệp
        srs_content = zf.read("01_SRS_Specification_IEEE29148.md").decode("utf-8")
        assert "# CineMax Cinema Management" in srs_content

        sql_content = zf.read("02_Database_Schema_3NF.sql").decode("utf-8")
        assert "CREATE TABLE seats" in sql_content

        csv_content = zf.read("03_Traceability_Matrix_RTM.csv")
        assert csv_content.startswith(b"\xef\xbb\xbf")

        seq_mmd = zf.read("diagrams/sequence_diagram.mmd").decode("utf-8")
        assert "Customer->>Server: Lock Seat" in seq_mmd

        state_mmd = zf.read("diagrams/state_machine.mmd").decode("utf-8")
        assert "stateDiagram-v2" in state_mmd
