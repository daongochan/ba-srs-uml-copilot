"""Reusable UI components for BA & System Architect Copilot.

Direction 3: Editorial Craft (Tài Liệu Biên Tập - GitBook / Craft).
All components adhere to tokens defined in src.ui.tokens.
"""

from typing import List, Optional, Union
import html
import streamlit as st

from src.models.srs_schema import FunctionalRequirement, SRSDocument
from src.services.telemetry_cache import TelemetryMetrics
from src.ui.theme import render_clean_html


def render_editorial_header(has_result: bool = False, current_step: int = 1) -> None:
    """Render the top Editorial Hero Banner with the 4-step BA workflow stepper."""
    step_num = 3 if has_result else current_step

    banner_html = """
    <div class="editorial-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1>📖 BA & System Architect Copilot</h1>
                <p>Nền tảng Tự động hóa Đặc tả Phần mềm chuẩn IEEE 29148, Mô hình Động UML & Thiết kế CSDL 3NF</p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 6px; padding: 4px 10px; font-size: 12px; font-weight: 600;">
                Phiên bản 2.0 • Editorial Craft
            </div>
        </div>
    </div>
    """
    render_clean_html(banner_html)

    # 4-Step Stepper
    steps = [
        (1, "1. Nhập yêu cầu"),
        (2, "2. Phân tích AI"),
        (3, "3. Rà soát kiến trúc"),
        (4, "4. Xuất bản hồ sơ"),
    ]

    stepper_items_html = []
    for num, label in steps:
        is_active = (num == step_num) or (has_result and num <= 3)
        active_cls = "active" if is_active else ""
        stepper_items_html.append(
            f'<div class="stepper-item {active_cls}">'
            f'<span class="stepper-num">{num}</span>'
            f'<span>{html.escape(label)}</span>'
            f'</div>'
        )

    stepper_html = f"""
    <div class="editorial-stepper">
        {'<span class="stepper-sep">→</span>'.join(stepper_items_html)}
    </div>
    """
    render_clean_html(stepper_html)


def render_editorial_kpi_strip(srs_doc: Optional[SRSDocument], telemetry: Optional[TelemetryMetrics] = None) -> None:
    """Render the top 4 business KPI cards in clean editorial layout."""
    if srs_doc is None:
        return

    # Calculate metrics
    num_stories = len(srs_doc.functional_requirements) if srs_doc.functional_requirements else 0
    rtm_count = len(srs_doc.traceability_matrix) if srs_doc.traceability_matrix else 0
    rtm_coverage_pct = 100.0 if (num_stories > 0 and rtm_count >= num_stories) else (
        round((rtm_count / num_stories) * 100, 1) if num_stories > 0 else 0.0
    )

    quality_score = 95
    invest_score = 100
    if hasattr(srs_doc, "quality_audit") and srs_doc.quality_audit:
        quality_score = getattr(srs_doc.quality_audit, "ieee_compliance_score", 95)
        invest_score = getattr(srs_doc.quality_audit, "invest_score", 100)

    kpi_html = f"""
    <div class="editorial-kpi-grid">
        <div class="editorial-kpi-card">
            <div class="editorial-kpi-title">Tiêu chuẩn IEEE 29148</div>
            <div class="editorial-kpi-val">{quality_score}/100</div>
            <div class="editorial-kpi-subtitle">Đặc tả hoàn chỉnh & khả thi</div>
        </div>
        <div class="editorial-kpi-card">
            <div class="editorial-kpi-title">Chỉ số INVEST</div>
            <div class="editorial-kpi-val">{invest_score}%</div>
            <div class="editorial-kpi-subtitle">User Stories sẵn sàng Sprint</div>
        </div>
        <div class="editorial-kpi-card">
            <div class="editorial-kpi-title">Chuỗi Truy Vết RTM</div>
            <div class="editorial-kpi-val">{rtm_coverage_pct}%</div>
            <div class="editorial-kpi-subtitle">{rtm_count}/{num_stories} Yêu cầu đã ánh xạ</div>
        </div>
        <div class="editorial-kpi-card">
            <div class="editorial-kpi-title">Quy Mô Nghiệp Vụ</div>
            <div class="editorial-kpi-val">{num_stories} Stories</div>
            <div class="editorial-kpi-subtitle">Kèm tiêu chí nghiệm thu BDD</div>
        </div>
    </div>
    """
    render_clean_html(kpi_html)


def render_editorial_story_card(
    req: Union[FunctionalRequirement, dict, str],
    title: str = "",
    user_story: str = "",
    priority: str = "Must Have",
    acceptance_criteria: Optional[List] = None,
) -> None:
    """Render a single User Story in Editorial Document Card style with BDD block."""
    if isinstance(req, FunctionalRequirement):
        r_id = req.req_id
        r_title = req.title
        r_story = req.user_story
        r_priority = req.priority or "Must Have"
        r_ac = req.acceptance_criteria or []
    elif isinstance(req, dict):
        r_id = req.get("req_id", "FR-XXX")
        r_title = req.get("title", title)
        r_story = req.get("user_story", user_story)
        r_priority = req.get("priority", priority)
        r_ac = req.get("acceptance_criteria", acceptance_criteria or [])
    else:
        r_id = str(req)
        r_title = title
        r_story = user_story
        r_priority = priority
        r_ac = acceptance_criteria or []

    # Priority badge class
    p_lower = r_priority.lower()
    if "must" in p_lower:
        badge_cls = "badge-must-have"
    elif "should" in p_lower:
        badge_cls = "badge-should-have"
    else:
        badge_cls = "badge-could-have"

    # Acceptance criteria items
    ac_rows = []
    for ac in r_ac:
        if hasattr(ac, "given"):
            given = getattr(ac, "given", "")
            when = getattr(ac, "when", "")
            then = getattr(ac, "then", "")
        elif isinstance(ac, dict):
            given = ac.get("given", "")
            when = ac.get("when", "")
            then = ac.get("then", "")
        else:
            given = str(ac)
            when = ""
            then = ""

        ac_rows.append(
            f'<div class="editorial-bdd-block">'
            f'<div><span class="bdd-kw">Given (Cho):</span> {html.escape(given)}</div>'
            f'<div><span class="bdd-kw">When (Khi):</span> {html.escape(when)}</div>'
            f'<div><span class="bdd-kw">Then (Thì):</span> {html.escape(then)}</div>'
            f'</div>'
        )

    ac_content = "".join(ac_rows) if ac_rows else '<div style="font-size: 12px; color: #78716c; font-style: italic; margin-top: 6px;">Chưa có tiêu chí nghiệm thu chi tiết.</div>'

    card_html = f"""
    <div class="editorial-card">
        <div class="editorial-card-header">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="editorial-card-id">{html.escape(r_id)}</span>
                <span class="editorial-card-title">{html.escape(r_title)}</span>
            </div>
            <span class="editorial-badge {badge_cls}">{html.escape(r_priority)}</span>
        </div>
        <div style="font-size: 13.5px; color: #292524; margin-bottom: 10px; line-height: 1.5;">
            {html.escape(r_story)}
        </div>
        <div style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #57534e; margin-top: 8px;">
            Tiêu chí nghiệm thu BDD (Acceptance Criteria):
        </div>
        {ac_content}
    </div>
    """
    render_clean_html(card_html)


def render_editorial_empty_state() -> None:
    """Render friendly empty state with clear next actions."""
    empty_html = """
    <div style="background: #ffffff; border: 1px dashed #d6d3d1; border-radius: 8px; padding: 40px 24px; text-align: center; margin: 20px 0;">
        <div style="font-size: 36px; margin-bottom: 12px;">📑</div>
        <div style="font-size: 16px; font-weight: 700; color: #1c1917; margin-bottom: 6px;">
            Chưa có hồ sơ đặc tả nào được khởi tạo
        </div>
        <div style="font-size: 13.5px; color: #57534e; max-width: 520px; margin: 0 auto 16px; line-height: 1.5;">
            Hãy chọn một <b>kịch bản khảo sát mẫu 1-click</b> phía trên hoặc dán biên bản họp yêu cầu của bạn vào khung văn bản, sau đó nhấn nút <b>"Phân tích Yêu cầu & Tạo Đặc tả"</b>.
        </div>
    </div>
    """
    render_clean_html(empty_html)


def render_editorial_tech_expander(
    telemetry: Optional[TelemetryMetrics],
    srs_doc: Optional[SRSDocument] = None,
) -> None:
    """Progressive disclosure expander for developer/architect telemetry and audits."""
    with st.expander("🔍 Chi tiết Kỹ thuật & Báo cáo Kiểm toán (Progressive Disclosure)", expanded=False):
        col_tel, col_audit = st.columns(2)

        with col_tel:
            st.markdown("##### ⚡ LLMOps Telemetry")
            if telemetry:
                st.markdown(
                    f"- **Độ trễ API**: `{telemetry.latency_ms:.1f} ms`\n"
                    f"- **Prompt Tokens**: `{telemetry.prompt_tokens:,}`\n"
                    f"- **Completion Tokens**: `{telemetry.completion_tokens:,}`\n"
                    f"- **Tổng Tokens**: `{telemetry.total_tokens:,}`\n"
                    f"- **Deterministic Cache Hit**: `{'Có (Tiết kiệm chi phí)' if telemetry.cache_hit else 'Không (Tạo mới)'}`\n"
                    f"- **Content SHA-256**: `{telemetry.content_hash[:16]}...`"
                )
            else:
                st.caption("Chưa có số liệu telemetry cho phiên chạy này.")

        with col_audit:
            st.markdown("##### 🛡️ Kiểm toán Chất lượng & CSDL")
            if srs_doc and hasattr(srs_doc, "quality_audit") and srs_doc.quality_audit:
                qa = srs_doc.quality_audit
                ieee_score = getattr(qa, "ieee_compliance_score", 90)
                inv_score = getattr(qa, "invest_score", 90)
                clarification_count = len(getattr(qa, "clarification_questions", []))
                st.markdown(
                    f"- **Điểm Tuân thủ IEEE 29148**: `{ieee_score}/100`\n"
                    f"- **Điểm INVEST**: `{inv_score}/100`\n"
                    f"- **Câu hỏi làm rõ nghiệp vụ**: `{clarification_count} câu hỏi`\n"
                    f"- **Chuẩn hóa CSDL 3NF**: `{'Đã giải trình' if getattr(qa, 'third_nf_justification', '') else 'Chưa có'}`"
                )
            else:
                st.caption("Chưa có dữ liệu kiểm toán cho tài liệu.")
