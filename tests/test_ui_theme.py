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
