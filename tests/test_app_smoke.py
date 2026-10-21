"""Smoke tests for Streamlit application using streamlit.testing.v1.AppTest."""

from pathlib import Path
from unittest.mock import patch
import pytest
from streamlit.testing.v1 import AppTest

from src.models.srs_schema import (
    SRSDocument,
    FunctionalRequirement,
    NonFunctionalRequirement,
    AcceptanceCriterion,
    TraceabilityItem,
    QualityAudit,
)
from src.services.telemetry_cache import TelemetryMetrics

APP_PATH = str(Path(__file__).parent.parent / "src" / "app.py")


def _build_test_srs_doc() -> SRSDocument:
    """Helper to build a valid sample SRSDocument for testing app tabs."""
    criterion = AcceptanceCriterion(
        given="Khách hàng đã đăng nhập và đang ở trang chọn suất chiếu",
        when="Khách hàng nhấn chọn ghế A1",
        then="Hệ thống đổi trạng thái ghế sang Đang giữ chỗ và bắt đầu đếm ngược 10 phút",
    )
    fr = FunctionalRequirement(
        req_id="FR-01",
        title="Khóa ghế tạm thời khi chọn chỗ",
        user_story="Là một khách hàng, tôi muốn giữ chỗ tạm thời trong 10 phút để hoàn tất thanh toán mà không bị người khác mua mất.",
        priority="High",
        acceptance_criteria=[criterion],
    )
    nfr = NonFunctionalRequirement(
        category="Performance",
        description="Thời gian phản hồi khi người dùng chọn và khóa ghế",
        metric="Response Time < 200ms với 3000 CCU",
    )
    seq = """sequenceDiagram
    actor Customer as "Khách hàng"
    participant Web as "Web App"
    Customer->>Web: Chọn ghế A1
"""
    er = """erDiagram
    SEATS {
        int id PK
        varchar seat_code
    }
"""
    sql = """
CREATE TABLE seats (
    id SERIAL PRIMARY KEY,
    seat_code VARCHAR(10) NOT NULL
);
"""
    rtm = [
        TraceabilityItem(
            req_id="FR-01",
            feature_name="Khóa ghế tạm thời",
            business_rule="Chỉ khóa ghế trong vòng 10 phút",
            related_tables=["seats"],
            test_scenario_summary="Kiểm thử xung đột khóa ghế",
        )
    ]
    audit = QualityAudit(
        ieee_compliance_score=95,
        invest_score=90,
        third_nf_justification="Bảng seats đã đạt chuẩn 3NF.",
        clarification_questions=[],
    )
    return SRSDocument(
        project_title="CineMax Booking System",
        business_objective="Tự động hóa quy trình đặt vé và tối ưu tỷ lệ lấp đầy rạp.",
        actors=["Khách hàng", "Nhân viên bán vé"],
        functional_requirements=[fr],
        non_functional_requirements=[nfr],
        sequence_diagram_mermaid=seq,
        state_diagram_mermaid="stateDiagram-v2\n    [*] --> Available\n    Available --> Locked : Select",
        state_machine_entity="Seat",
        er_diagram_mermaid=er,
        sql_ddl_script=sql,
        traceability_matrix=rtm,
        quality_audit=audit,
    )


def test_app_initial_cold_start():
    """Verify app starts cleanly without unhandled exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception, f"App crashed on cold start: {at.exception}"
    assert len(at.markdown) > 0


def test_app_generate_without_api_key_shows_error(monkeypatch):
    """Verify clicking generate button without an API key surfaces an informative error."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with patch("dotenv.load_dotenv", return_value=False):
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()

        for ti in at.sidebar.text_input:
            ti.set_value("")

        for btn in at.button:
            if "Phân tích" in getattr(btn, "label", ""):
                btn.click().run()
                break

        errors = [err.value for err in at.error]
        assert any("Gemini API Key" in e for e in errors)


def test_app_renders_all_tabs_with_srs_result():
    """Verify that when srs_result is present in session_state, all 4 tabs render without crash."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    doc = _build_test_srs_doc()
    at.session_state["srs_result"] = doc
    at.run()
    assert not at.exception, f"App crashed when rendering tabs: {at.exception}"
    subheaders = [s.value for s in at.subheader]
    assert any("CineMax Booking System" in s for s in subheaders)
    assert len(at.tabs) >= 4


def test_app_sidebar_clear_cache():
    """Verify that clicking the clear cache button executes without error."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    for btn in at.sidebar.button:
        if "Xóa Bộ nhớ đệm" in getattr(btn, "label", ""):
            btn.click().run()
            break
    assert not at.exception


def test_app_load_sample_scenario():
    """Verify selecting a built-in scenario and clicking load populates raw_notes_input."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()

    # Find selectbox in sidebar and select bus_logistics, then run
    for sb in at.sidebar.selectbox:
        if "kịch bản" in getattr(sb, "label", "").lower():
            sb.select("bus_logistics").run()
            break

    # Now click load button and run
    for btn in at.sidebar.button:
        if "Nạp kịch bản này" in getattr(btn, "label", ""):
            btn.click().run()
            break

    assert not at.exception
    raw_notes = at.session_state.get("raw_notes_input", "")
    assert "Xe khách" in raw_notes or "Phương Nam" in raw_notes


def test_app_meeting_notes_input_has_max_chars_guardrail():
    """Verify that the raw meeting notes text area enforces max_chars guardrail of 50,000."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert len(at.text_area) >= 1
    assert at.text_area[0].proto.max_chars == 50000
