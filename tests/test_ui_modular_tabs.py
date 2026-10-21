"""Unit tests for modularized UI components and tabs."""

from unittest.mock import patch, MagicMock
import pytest
from src.models.srs_schema import (
    SRSDocument,
    FunctionalRequirement,
    NonFunctionalRequirement,
    AcceptanceCriterion,
    TraceabilityItem,
    QualityAudit,
)
from src.ui.components.mermaid_viewer import render_mermaid
from src.ui.tabs import (
    render_tab_srs_requirements,
    render_tab_dynamic_models,
    render_tab_database_design,
    render_tab_export_bundle,
)


def _build_test_doc() -> SRSDocument:
    """Helper to build a valid sample SRSDocument for unit tests."""
    return SRSDocument(
        project_title="Cinema Booking",
        business_objective="Tối ưu đặt vé trực tuyến",
        actors=["Khách hàng"],
        functional_requirements=[
            FunctionalRequirement(
                req_id="FR-01",
                title="Khóa ghế",
                user_story="Là một khách hàng, tôi muốn giữ chỗ tạm thời trong 10 phút.",
                priority="High",
                acceptance_criteria=[
                    AcceptanceCriterion(
                        given="Đang chọn ghế",
                        when="Bấm chọn ghế A1",
                        then="Ghế chuyển sang trạng thái đã giữ chỗ",
                    )
                ],
            )
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(
                category="Performance",
                description="Thời gian phản hồi nhanh",
                metric="< 200ms",
            )
        ],
        sequence_diagram_mermaid='sequenceDiagram\n    actor U as "User"\n    U->>S: Request',
        state_diagram_mermaid="stateDiagram-v2\n    [*] --> Available\n    Available --> Locked : Select",
        state_machine_entity="Seat",
        er_diagram_mermaid="erDiagram\n    SEATS {\n        int id PK\n        varchar code\n    }",
        sql_ddl_script="CREATE TABLE seats (id INT PRIMARY KEY, code VARCHAR(10));",
        traceability_matrix=[
            TraceabilityItem(
                req_id="FR-01",
                feature_name="Khóa ghế",
                business_rule="Giữ trong 10 phút",
                related_tables=["seats"],
                test_scenario_summary="Kiểm thử giữ chỗ",
            )
        ],
        quality_audit=QualityAudit(
            ieee_compliance_score=95,
            invest_score=90,
            third_nf_justification="Bảng seats đạt chuẩn 3NF.",
            clarification_questions=["Cần xác nhận thời gian timeout?"],
        ),
    )


def test_public_api_backward_compatibility():
    """Verify src.app maintains backward compatible imports."""
    from src.app import render_mermaid as app_render_mermaid
    from src.app import export_srs_markdown as app_export_srs_markdown

    assert callable(app_render_mermaid)
    assert callable(app_export_srs_markdown)


def test_render_mermaid_calls_components_html():
    """Verify render_mermaid cleans code and outputs interactive html component."""
    with patch("streamlit.components.v1.html") as mock_html:
        render_mermaid("sequenceDiagram\n    U->>S: req", height=500, diagram_type="sequenceDiagram")
        mock_html.assert_called_once()
        html_arg = mock_html.call_args[0][0]
        assert "mermaid.initialize" in html_arg
        assert "securityLevel: 'strict'" in html_arg


def test_render_tab_srs_requirements_runs_cleanly():
    """Verify Tab 1 renders without error."""
    doc = _build_test_doc()
    with (
        patch("streamlit.markdown"),
        patch("streamlit.info"),
        patch("streamlit.warning"),
        patch("streamlit.success"),
        patch("streamlit.table"),
        patch("streamlit.dataframe"),
        patch("streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()]),
    ):
        render_tab_srs_requirements(doc)


def test_render_tab_dynamic_models_runs_cleanly():
    """Verify Tab 2 renders sequence and state diagrams."""
    doc = _build_test_doc()
    with (
        patch("streamlit.markdown"),
        patch("streamlit.caption"),
        patch("streamlit.divider"),
        patch("streamlit.expander"),
        patch("src.ui.tabs.tab_dynamic_models.render_mermaid") as mock_render,
    ):
        render_tab_dynamic_models(doc)
        assert mock_render.call_count == 2


def test_render_tab_database_design_runs_cleanly():
    """Verify Tab 3 renders ERD, SQL DDL, and Sandbox audit."""
    doc = _build_test_doc()
    with (
        patch("streamlit.markdown"),
        patch("streamlit.caption"),
        patch("streamlit.code"),
        patch("streamlit.expander"),
        patch("streamlit.columns", return_value=[MagicMock(), MagicMock()]),
        patch("src.ui.tabs.tab_database.render_mermaid"),
    ):
        render_tab_database_design(doc)


def test_render_tab_export_bundle_runs_cleanly():
    """Verify Tab 4 renders download buttons and preview tabs."""
    doc = _build_test_doc()
    with (
        patch("streamlit.markdown"),
        patch("streamlit.caption"),
        patch("streamlit.download_button"),
        patch("streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock(), MagicMock()]),
        patch("streamlit.tabs", return_value=[MagicMock(), MagicMock()]),
    ):
        render_tab_export_bundle(doc)
