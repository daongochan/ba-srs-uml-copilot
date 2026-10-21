"""Unit tests for UI Theme and Design System components."""

import pytest
from src.models.srs_schema import FunctionalRequirement, AcceptanceCriterion
from src.services.telemetry_cache import TelemetryMetrics
from src.ui.theme import (
    apply_custom_theme,
    render_header_banner,
    render_bento_card,
    render_bento_grid,
    render_telemetry_widget,
    render_user_story_card,
    render_clean_html,
    render_html,
    render_kpi_card,
)


def test_render_bento_card():
    html = render_bento_card(
        title="Tuân thủ IEEE 29148",
        value="95/100",
        subtitle="Kiểm định Xác định",
        score_pct=95.0,
        badge_text="Chuẩn Hóa",
        badge_type="success",
        icon="📐",
    )
    assert "bento-card" in html
    assert "Tuân thủ IEEE 29148" in html
    assert "95/100" in html
    assert "bento-progress-bar" in html
    assert "width: 95.0%" in html
    assert "Chuẩn Hóa" in html


def test_render_bento_grid():
    # Test with both dicts and pre-rendered strings
    cards = [
        {
            "title": "Metric 1",
            "value": "100%",
            "subtitle": "Sub 1",
            "score_pct": 100.0,
        },
        render_bento_card(title="Metric 2", value="50", subtitle="Sub 2"),
    ]
    # Streamlit markdown call shouldn't raise exception
    render_bento_grid(cards)


def test_render_telemetry_widget():
    metrics = TelemetryMetrics(
        latency_ms=45.2,
        prompt_tokens=1200,
        completion_tokens=850,
        total_tokens=2050,
        cache_hit=True,
        retry_attempts=0,
        content_hash="abc123def4567890",
        timestamp="2026-10-21T09:00:00",
    )
    # Should render without raising
    render_telemetry_widget(metrics)
    # None telemetry should safely early-return
    render_telemetry_widget(None)


def test_render_user_story_card():
    # Test with model object
    fr = FunctionalRequirement(
        req_id="FR-001",
        title="Khóa ghế tạm thời",
        user_story="Là Khách hàng, tôi muốn khóa ghế để thanh toán",
        priority="Must Have",
        acceptance_criteria=[
            AcceptanceCriterion(
                given="Ghế đang trống",
                when="Người dùng bấm chọn ghế",
                then="Ghế chuyển sang trạng thái Locked trong 10 phút",
            )
        ],
    )
    render_user_story_card(fr)

    # Test with raw arguments
    render_user_story_card(
        req_or_id="FR-002",
        title="Hủy vé xem phim",
        user_story="Là Khách hàng, tôi muốn hủy vé",
        priority="Could Have",
        acceptance_criteria=[],
    )


def test_theme_functions_smoke():
    # Smoke tests for theme application and header
    apply_custom_theme()
    render_header_banner(has_result=False)
    render_header_banner(has_result=True)


def test_render_html_prevents_commonmark_indentation_leak():
    """Verify render_clean_html (and alias render_html) strips leading line spaces and consecutive blank lines."""
    from unittest.mock import patch

    with patch("streamlit.markdown") as mock_markdown:
        raw_indented_html = """
        <div class="test-container">
            <div class="bento-progress-track">
                <span>Value</span>
            </div>
        </div>
        """
        render_clean_html(raw_indented_html)
        mock_markdown.assert_called_once()
        passed_arg = mock_markdown.call_args[0][0]
        # Should not have any line starting with 4 or more spaces
        for line in passed_arg.splitlines():
            assert not line.startswith("    "), f"Line still indented with 4 spaces: {line}"
        assert '<div class="test-container">' in passed_arg
        assert mock_markdown.call_args[1].get("unsafe_allow_html") is True

    # Test alias render_html works identically
    with patch("streamlit.markdown") as mock_markdown2:
        render_html("<p>test</p>")
        mock_markdown2.assert_called_once_with("<p>test</p>", unsafe_allow_html=True)


def test_render_kpi_card():
    """Verify render_kpi_card renders directly through render_clean_html."""
    from unittest.mock import patch

    with patch("src.ui.theme.render_clean_html") as mock_render_html:
        render_kpi_card(
            title="SLA Performance",
            value="99.9%",
            subtitle="Uptime Guarantee",
            score_pct=99.9,
            badge_text="Gold SLA",
            badge_type="success",
            icon="⚡",
        )
        mock_render_html.assert_called_once()
        rendered_card = mock_render_html.call_args[0][0]
        assert "SLA Performance" in rendered_card
        assert "99.9%" in rendered_card


def test_editorial_tokens_and_styles():
    """Verify editorial tokens definitions and style injection."""
    from src.ui import tokens
    from src.ui.styles import apply_editorial_styles, EDITORIAL_CSS
    from unittest.mock import patch

    assert tokens.TEAL_600 == "#0D9488"
    assert tokens.STONE_50 == "#FAFAF9"
    assert "Be Vietnam Pro" in tokens.FONT_PRIMARY
    assert "editorial-banner" in EDITORIAL_CSS

    with patch("streamlit.markdown") as mock_markdown:
        apply_editorial_styles()
        mock_markdown.assert_called_once()


def test_editorial_components_render():
    """Verify editorial header, kpi strip, story card, and empty state."""
    from src.ui.components import (
        render_editorial_header,
        render_editorial_kpi_strip,
        render_editorial_story_card,
        render_editorial_empty_state,
        render_editorial_tech_expander,
    )
    from tests.test_ui_modular_tabs import _build_test_doc
    from unittest.mock import patch

    with patch("src.ui.components.editorial.render_clean_html") as mock_html:
        render_editorial_header(has_result=False, current_step=1)
        assert mock_html.called

    with patch("src.ui.components.editorial.render_clean_html") as mock_html:
        doc = _build_test_doc()
        render_editorial_kpi_strip(doc)
        assert mock_html.called

    with patch("src.ui.components.editorial.render_clean_html") as mock_html:
        doc = _build_test_doc()
        render_editorial_story_card(doc.functional_requirements[0])
        assert mock_html.called

    with patch("src.ui.components.editorial.render_clean_html") as mock_html:
        render_editorial_empty_state()
        assert mock_html.called

    # Tech expander smoke test
    render_editorial_tech_expander(None, None)


