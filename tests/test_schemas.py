"""Unit tests for Pydantic SRS Schemas."""

import pytest
from src.models.srs_schema import (
    AcceptanceCriterion,
    FunctionalRequirement,
    NonFunctionalRequirement,
    SRSDocument,
)


def test_srs_document_instantiation_and_validation():
    criterion = AcceptanceCriterion(
        given="Khách hàng đã đăng nhập và đang ở trang chọn suất chiếu",
        when="Khách hàng nhấn chọn ghế A1",
        then="Hệ thống đổi trạng thái ghế sang Đang giữ chỗ và bắt đầu đếm ngược 10 phút",
    )

    fr = FunctionalRequirement(
        req_id="FR-01",
        title="Khóa ghế tạm thời khi chọn chỗ",
        user_story="Là khách hàng, tôi muốn giữ chỗ tạm thời trong 10 phút để thanh toán mà không bị người khác mua mất.",
        priority="High",
        acceptance_criteria=[criterion],
    )

    nfr = NonFunctionalRequirement(
        category="Performance",
        description="Thời gian phản hồi khi người dùng chọn và khóa ghế",
        metric="Response Time < 200ms với 3000 CCU",
    )

    doc = SRSDocument(
        project_title="CineMax Booking System",
        business_objective="Tự động hóa quy trình đặt vé và tối ưu tỷ lệ lấp đầy rạp.",
        actors=["Khách hàng", "Nhân viên bán vé", "Hệ thống Thanh toán"],
        functional_requirements=[fr],
        non_functional_requirements=[nfr],
        sequence_diagram_mermaid="sequenceDiagram\n  KhachHang->>Server: Chon ghe",
        er_diagram_mermaid="erDiagram\n  CUSTOMER ||--o{ TICKET : buys",
        sql_ddl_script="CREATE TABLE tickets (id SERIAL PRIMARY KEY, seat_code VARCHAR(10));",
    )

    assert doc.project_title == "CineMax Booking System"
    assert len(doc.functional_requirements) == 1
    assert doc.functional_requirements[0].req_id == "FR-01"
    assert len(doc.non_functional_requirements) == 1
    assert len(doc.actors) == 3

    # Test serialization to dict and JSON
    data_dict = doc.model_dump()
    assert data_dict["project_title"] == "CineMax Booking System"
    json_str = doc.model_dump_json()
    assert "FR-01" in json_str
