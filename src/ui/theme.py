"""Enterprise UI Theme and Design Tokens for BA & System Architect Copilot.

Based on UI/UX Pro Max Design Intelligence (Tech & SaaS -> Developer Tool / IDE & B2B Service).
"""

import html
import re
from typing import List, Dict, Any, Optional
import streamlit as st


def render_clean_html(raw_html: str) -> None:
    """Loại bỏ thụt lề đầu dòng và các dòng trống thừa trước khi gọi st.markdown.

    Biện pháp này triệt tiêu hoàn toàn lỗi CommonMark hiểu nhầm chuỗi HTML
    thành Markdown Indented Code Block (<pre><code>) khi có dòng trống đi kèm thụt lề >= 4 spaces.
    """
    if not raw_html:
        return
    # Loại bỏ khoảng trắng / tab ở đầu mỗi dòng
    cleaned = re.sub(r"^[ \t]+", "", raw_html, flags=re.MULTILINE)
    # Loại bỏ các dòng trống liên tiếp
    cleaned = re.sub(r"\n\s*\n", "\n", cleaned).strip()
    st.markdown(cleaned, unsafe_allow_html=True)


# Alias tương thích ngược
render_html = render_clean_html


def apply_custom_theme() -> None:
    """Nạp toàn bộ CSS Design Tokens và ghi đè giao diện Streamlit theo chuẩn Enterprise SaaS IDE."""
    custom_css = """
    <style>
        /* =====================================================================
           1. GOOGLE FONTS & DESIGN TOKENS
           ===================================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {
            --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;

            /* Surface Colors (Enterprise Slate) */
            --bg-main: #f8fafc;
            --bg-surface: #ffffff;
            --bg-muted: #f1f5f9;
            --border-subtle: #e2e8f0;
            --border-strong: #cbd5e1;

            /* Primary Brand (Royal Indigo) */
            --brand-primary: #4f46e5;
            --brand-primary-hover: #4338ca;
            --brand-primary-light: #eef2ff;
            --brand-primary-border: #c7d2fe;

            /* Semantic Status Tokens */
            --status-success: #10b981;
            --status-success-bg: #ecfdf5;
            --status-success-border: #a7f3d0;

            --status-warning: #f59e0b;
            --status-warning-bg: #fffbeb;
            --status-warning-border: #fde68a;

            --status-danger: #e11d48;
            --status-danger-bg: #fff1f2;
            --status-danger-border: #fecdd3;

            --status-info: #0284c7;
            --status-info-bg: #f0f9ff;
            --status-info-border: #bae6fd;

            /* Text Tokens */
            --text-heading: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --text-dim: #94a3b8;

            /* Shadow Layers */
            --shadow-xs: 0 1px 2px 0 rgba(15, 23, 42, 0.05);
            --shadow-sm: 0 1px 3px 0 rgba(15, 23, 42, 0.07), 0 1px 2px -1px rgba(15, 23, 42, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
            --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.03);
            --radius-md: 8px;
            --radius-lg: 12px;
        }

        /* =====================================================================
           2. GLOBAL STREAMLIT OVERRIDES
           ===================================================================== */
        html, body, [class*="css"] {
            font-family: var(--font-sans) !important;
            color: var(--text-body);
        }

        /* Nền ứng dụng chính */
        .stApp {
            background-color: var(--bg-main) !important;
        }

        /* Typography Heading Overrides */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-sans) !important;
            font-weight: 700 !important;
            color: var(--text-heading) !important;
            letter-spacing: -0.02em;
        }

        code, pre, .stCodeBlock {
            font-family: var(--font-mono) !important;
        }

        /* =====================================================================
           3. TOP NAVIGATION BANNER (HIGH-CONTRAST LIGHT INDIGO SURFACE)
           ===================================================================== */
        .workbench-header {
            background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 100%) !important;
            border: 1px solid #c7d2fe !important;
            border-radius: var(--radius-lg);
            padding: 22px 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 14px -2px rgba(79, 70, 229, 0.08), 0 1px 3px rgba(15, 23, 42, 0.05);
        }

        .header-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 16px;
        }

        .brand-title-wrap {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-logo-badge {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25);
            flex-shrink: 0;
        }

        .brand-title {
            font-size: 24px !important;
            font-weight: 800 !important;
            color: #1e1b4b !important;
            margin: 0 !important;
            line-height: 1.25 !important;
            letter-spacing: -0.025em;
        }

        .brand-subtitle {
            font-size: 13.5px !important;
            color: #475569 !important;
            margin: 4px 0 0 0 !important;
            font-weight: 500 !important;
        }

        .standards-pill-group {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .standard-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: #334155;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }

        .standard-pill.model-pill {
            background: #eff6ff;
            border-color: #bfdbfe;
            color: #1d4ed8;
        }

        .standard-pill.ieee-pill {
            background: #fdf4ff;
            border-color: #f5d0fe;
            color: #86198f;
        }

        .standard-pill.babok-pill {
            background: #f0fdf4;
            border-color: #bbf7d0;
            color: #166534;
        }

        .standard-pill.sandbox-pill {
            background: #fff7ed;
            border-color: #fed7aa;
            color: #9a3412;
        }

        /* Workflow Stepper */
        .workflow-stepper {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 10px;
            padding: 10px 14px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-md);
            margin-top: 14px;
        }

        .step-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 12px;
            color: #64748b;
            font-weight: 500;
        }

        .step-item.active {
            background: #eef2ff;
            color: #4f46e5;
            font-weight: 700;
        }

        .step-item.completed {
            background: #ecfdf5;
            color: #059669;
            font-weight: 600;
        }

        .step-number {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #f1f5f9;
            color: #64748b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
        }

        .step-item.active .step-number {
            background: #4f46e5;
            color: #ffffff;
        }

        .step-item.completed .step-number {
            background: #10b981;
            color: #ffffff;
        }

        /* =====================================================================
           4. BENTO KPI GRID DASHBOARD
           ===================================================================== */
        .bento-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 16px 18px;
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 135px;
            height: 100%;
            transition: all 0.2s ease;
        }

        .bento-card:hover {
            border-color: var(--brand-primary-border);
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }

        .bento-card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
            gap: 8px;
        }

        .bento-title {
            font-size: 12px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .bento-badge {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            white-space: nowrap;
        }

        .bento-badge.success {
            background: var(--status-success-bg);
            color: var(--status-success);
            border: 1px solid var(--status-success-border);
        }

        .bento-badge.warning {
            background: var(--status-warning-bg);
            color: var(--status-warning);
            border: 1px solid var(--status-warning-border);
        }

        .bento-badge.danger {
            background: var(--status-danger-bg);
            color: var(--status-danger);
            border: 1px solid var(--status-danger-border);
        }

        .bento-badge.info {
            background: var(--brand-primary-light);
            color: var(--brand-primary);
            border: 1px solid var(--brand-primary-border);
        }

        .bento-value {
            font-size: 28px !important;
            font-weight: 800 !important;
            color: var(--text-heading) !important;
            line-height: 1.15 !important;
            margin: 4px 0 !important;
            letter-spacing: -0.02em;
        }

        .bento-subtitle {
            font-size: 11.5px;
            color: var(--text-muted);
            margin-bottom: 10px;
            line-height: 1.4;
        }

        .bento-progress-track {
            width: 100%;
            height: 6px;
            background: var(--bg-muted);
            border-radius: 3px;
            overflow: hidden;
            margin-top: auto;
        }

        .bento-progress-bar {
            height: 100%;
            border-radius: 3px;
            transition: width 0.4s ease;
        }

        .bento-progress-bar.success { background: linear-gradient(90deg, #10b981, #059669); }
        .bento-progress-bar.warning { background: linear-gradient(90deg, #f59e0b, #d97706); }
        .bento-progress-bar.danger { background: linear-gradient(90deg, #e11d48, #be123c); }
        .bento-progress-bar.info { background: linear-gradient(90deg, #4f46e5, #3b82f6); }

        /* =====================================================================
           5. SIDEBAR & TELEMETRY PANEL (CLEAN VERTICAL STACKROWS)
           ===================================================================== */
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid var(--border-subtle) !important;
        }

        .telemetry-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: var(--radius-md);
            padding: 14px;
            margin-top: 10px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }

        .telemetry-status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.04em;
            margin-bottom: 10px;
            width: 100%;
            justify-content: center;
        }

        .telemetry-status-badge.hit {
            background: #ecfdf5;
            color: #059669;
            border: 1px solid #a7f3d0;
        }

        .telemetry-status-badge.live {
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
        }

        .telemetry-stack {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 10px;
        }

        .telemetry-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
            border-bottom: 1px dashed #e2e8f0;
            font-size: 12px;
        }

        .telemetry-row:last-child {
            border-bottom: none;
        }

        .telemetry-row-total {
            font-weight: 700;
            color: #0f172a;
            border-top: 1px solid #cbd5e1;
            padding-top: 6px;
            margin-top: 2px;
        }

        .telemetry-row-label {
            color: #475569;
            font-size: 11.5px;
        }

        .telemetry-row-val {
            font-family: var(--font-mono);
            font-weight: 700;
            color: #0f172a;
            font-size: 12px;
        }

        .telemetry-token-bar-wrap {
            background: #e2e8f0;
            border-radius: 4px;
            height: 6px;
            overflow: hidden;
            margin: 6px 0 10px 0;
            display: flex;
        }

        .token-prompt-fill { background: #3b82f6; height: 100%; }
        .token-completion-fill { background: #10b981; height: 100%; }

        .telemetry-hash-box {
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 6px;
        }

        .telemetry-hash-code {
            font-family: var(--font-mono);
            font-size: 11px;
            background: #e2e8f0;
            padding: 2px 6px;
            border-radius: 4px;
            color: #334155;
            font-weight: 600;
        }

        /* =====================================================================
           6. USER STORY & GHERKIN BDD CARDS
           ===================================================================== */
        .story-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-left: 4px solid var(--brand-primary);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            margin-bottom: 14px;
            box-shadow: var(--shadow-xs);
        }

        .story-card.must-have { border-left-color: var(--status-danger); }
        .story-card.should-have { border-left-color: var(--status-warning); }
        .story-card.could-have { border-left-color: var(--status-info); }

        .story-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .story-req-id {
            font-family: var(--font-mono);
            font-size: 13px;
            font-weight: 700;
            color: var(--brand-primary);
        }

        .story-title {
            font-size: 16px;
            font-weight: 700;
            color: var(--text-heading);
            margin: 0 0 6px 0;
        }

        .story-narrative {
            font-size: 13.5px;
            line-height: 1.5;
            color: var(--text-body);
            background: var(--bg-muted);
            padding: 10px 14px;
            border-radius: var(--radius-md);
            margin-bottom: 12px;
            font-style: italic;
        }

        /* Gherkin BDD Blocks */
        .gherkin-box {
            background: #ffffff;
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 12px 14px;
            margin-top: 8px;
            font-size: 13px;
        }

        .gherkin-line {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 4px;
            line-height: 1.5;
        }

        .gherkin-line:last-child {
            margin-bottom: 0;
        }

        .gherkin-token {
            font-family: var(--font-mono);
            font-weight: 700;
            font-size: 11px;
            padding: 1px 6px;
            border-radius: 4px;
            min-width: 48px;
            text-align: center;
            flex-shrink: 0;
        }

        .token-given { background: #fef3c7; color: #b45309; }
        .token-when { background: #e0f2fe; color: #0369a1; }
        .token-then { background: #dcfce7; color: #15803d; }

        /* =====================================================================
           7. STREAMLIT TABS STYLING (IDE DEVELOPER TOOLBAR)
           ===================================================================== */
        div[data-testid="stTabs"] button[role="tab"] {
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            color: var(--text-muted) !important;
            padding: 10px 18px !important;
            border-radius: 8px 8px 0 0 !important;
            transition: all 0.2s ease !important;
            border-bottom: 2px solid transparent !important;
        }

        div[data-testid="stTabs"] button[role="tab"]:hover {
            color: var(--brand-primary) !important;
            background-color: rgba(79, 70, 229, 0.04) !important;
        }

        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: var(--brand-primary) !important;
            border-bottom: 2px solid var(--brand-primary) !important;
            background-color: var(--brand-primary-light) !important;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_header_banner(has_result: bool = False) -> None:
    """Hiển thị Header Bar thương hiệu và Workflow Stepper chuẩn Enterprise, độ tương phản cao."""
    step1_class = "completed" if has_result else "active"
    step2_class = "completed" if has_result else ""
    step3_class = "active" if has_result else ""
    step4_class = "active" if has_result else ""

    banner_html = f"""<div class="workbench-header">
<div class="header-top-row">
<div class="brand-title-wrap">
<div class="brand-logo-badge">📐</div>
<div>
<h1 class="brand-title">BA & System Architect Copilot</h1>
<p class="brand-subtitle">Enterprise Requirements Engineering, Dynamic UML & 3NF Database Workbench</p>
</div>
</div>
<div class="standards-pill-group">
<span class="standard-pill model-pill">🤖 gemini-3.8-flash</span>
<span class="standard-pill ieee-pill">📋 IEEE 29148:2018</span>
<span class="standard-pill babok-pill">🏛️ BABOK v3</span>
<span class="standard-pill sandbox-pill">🗄️ 3NF Sandbox</span>
</div>
</div>
<div class="workflow-stepper">
<div class="step-item {step1_class}">
<span class="step-number">1</span>
<span>1. Elicitation Notes</span>
</div>
<div class="step-item {step2_class}">
<span class="step-number">2</span>
<span>2. AI Synthesis</span>
</div>
<div class="step-item {step3_class}">
<span class="step-number">3</span>
<span>3. Deterministic Audit</span>
</div>
<div class="step-item {step4_class}">
<span class="step-number">4</span>
<span>4. Export Bundle</span>
</div>
</div>
</div>"""
    render_clean_html(banner_html)


def render_bento_card(
    title: str,
    value: str,
    subtitle: str,
    score_pct: Optional[float] = None,
    badge_text: Optional[str] = None,
    badge_type: str = "info",
    icon: Optional[str] = None,
) -> str:
    """Tạo mã HTML cho một thẻ Bento KPI Card, bảo đảm không có khoảng thụt lề thừa hay dòng trống."""
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_subtitle = html.escape(str(subtitle))
    icon_str = f"{html.escape(str(icon))} " if icon else ""
    badge_html = ""
    if badge_text:
        safe_badge_type = html.escape(str(badge_type))
        safe_badge_text = html.escape(str(badge_text))
        badge_html = f'<span class="bento-badge {safe_badge_type}">{safe_badge_text}</span>'

    progress_html = ""
    if score_pct is not None:
        capped_pct = max(0.0, min(100.0, float(score_pct)))
        color_class = "success" if capped_pct >= 90 else ("warning" if capped_pct >= 75 else "danger")
        progress_html = (
            f'<div class="bento-progress-track">'
            f'<div class="bento-progress-bar {color_class}" style="width: {capped_pct}%;"></div>'
            f"</div>"
        )

    card_html = (
        f'<div class="bento-card">'
        f"<div>"
        f'<div class="bento-card-top">'
        f'<span class="bento-title">{icon_str}{safe_title}</span>'
        f"{badge_html}"
        f"</div>"
        f'<div class="bento-value">{safe_value}</div>'
        f'<div class="bento-subtitle">{safe_subtitle}</div>'
        f"</div>"
        f"{progress_html}"
        f"</div>"
    )
    return card_html


def render_kpi_card(
    title: str,
    value: str,
    subtitle: str,
    score_pct: Optional[float] = None,
    badge_text: Optional[str] = None,
    badge_type: str = "info",
    icon: Optional[str] = None,
) -> None:
    """Hiển thị một thẻ Bento KPI Card riêng lẻ bằng render_html."""
    html_card = render_bento_card(
        title=title,
        value=value,
        subtitle=subtitle,
        score_pct=score_pct,
        badge_text=badge_text,
        badge_type=badge_type,
        icon=icon,
    )
    render_clean_html(html_card)


def render_bento_grid(cards: List[Any]) -> None:
    """Hiển thị lưới Bento KPI Cards bằng st.columns(4) và render_clean_html riêng biệt cho từng cột."""
    if not cards:
        return
    cols = st.columns(len(cards))
    for col, item in zip(cols, cards):
        with col:
            if isinstance(item, str):
                render_clean_html(item)
            elif isinstance(item, dict):
                render_clean_html(render_bento_card(**item))


def render_telemetry_widget(telemetry: Any) -> None:
    """Hiển thị widget giám sát LLMOps Telemetry ở Sidebar theo bố cục Vertical StackRows trên nền sáng."""
    if not telemetry:
        return
    is_hit = getattr(telemetry, "cache_hit", False)
    latency_ms = getattr(telemetry, "latency_ms", 0.0)
    retries = getattr(telemetry, "retry_attempts", 0)
    prompt_tokens = getattr(telemetry, "prompt_tokens", 0)
    completion_tokens = getattr(telemetry, "completion_tokens", 0)
    total_tokens = getattr(telemetry, "total_tokens", 0)
    content_hash = getattr(telemetry, "content_hash", "")

    status_class = "hit" if is_hit else "live"
    status_text = "⚡ CACHE HIT (O(1) Memory)" if is_hit else "🌐 LIVE GEMINI API"

    latency_str = f"{latency_ms / 1000.0:.2f} s" if latency_ms >= 1000 else f"{latency_ms:.1f} ms"

    # Tính tỷ lệ token
    prompt_pct = (prompt_tokens / total_tokens * 100) if total_tokens else 50
    completion_pct = 100 - prompt_pct

    safe_hash = html.escape(str(content_hash)[:16])

    html_str = f"""<div class="telemetry-card">
<div class="telemetry-status-badge {status_class}">
{status_text}
</div>
<div class="telemetry-stack">
<div class="telemetry-row">
<span class="telemetry-row-label">⏱️ Độ trễ (Latency)</span>
<span class="telemetry-row-val">{latency_str}</span>
</div>
<div class="telemetry-row">
<span class="telemetry-row-label">🔄 Thử lại (Retries)</span>
<span class="telemetry-row-val">{retries} lần</span>
</div>
<div class="telemetry-row">
<span class="telemetry-row-label">📥 Input Prompt</span>
<span class="telemetry-row-val">{prompt_tokens:,} tok</span>
</div>
<div class="telemetry-row">
<span class="telemetry-row-label">📤 Output Completion</span>
<span class="telemetry-row-val">{completion_tokens:,} tok</span>
</div>
<div class="telemetry-row telemetry-row-total">
<span class="telemetry-row-label">🪙 Tổng Tokens</span>
<span class="telemetry-row-val">{total_tokens:,} tok</span>
</div>
</div>
<div class="telemetry-token-bar-wrap">
<div class="token-prompt-fill" style="width: {prompt_pct}%;" title="Prompt Tokens"></div>
<div class="token-completion-fill" style="width: {completion_pct}%;" title="Completion Tokens"></div>
</div>
<div class="telemetry-hash-box">
<span style="font-size: 11px; color: #64748b; font-weight: 600;">🔑 Khóa đệm SHA-256:</span>
<span class="telemetry-hash-code">{safe_hash}...</span>
</div>
</div>"""
    render_clean_html(html_str)


def render_user_story_card(
    req_or_id: Any,
    title: Optional[str] = None,
    user_story: Optional[str] = None,
    priority: Optional[str] = None,
    acceptance_criteria: Optional[List[Any]] = None,
) -> None:
    """Hiển thị thẻ User Story chuẩn MoSCoW kèm kịch bản Gherkin BDD."""
    if hasattr(req_or_id, "req_id"):
        raw_req_id = req_or_id.req_id
        raw_title = title or getattr(req_or_id, "title", "")
        raw_user_story = user_story or getattr(req_or_id, "user_story", "")
        raw_priority = priority or getattr(req_or_id, "priority", "Medium")
        raw_ac = acceptance_criteria or getattr(req_or_id, "acceptance_criteria", [])
    else:
        raw_req_id = str(req_or_id)
        raw_title = title or ""
        raw_user_story = user_story or ""
        raw_priority = priority or "Medium"
        raw_ac = acceptance_criteria or []

    req_id = html.escape(str(raw_req_id))
    safe_title = html.escape(str(raw_title))
    safe_user_story = html.escape(str(raw_user_story))
    safe_priority = html.escape(str(raw_priority))

    prio_class = "must-have"
    prio_badge_type = "danger"
    prio_lower = (raw_priority or "medium").lower()
    if "should" in prio_lower or "medium" in prio_lower:
        prio_class = "should-have"
        prio_badge_type = "warning"
    elif "could" in prio_lower or "low" in prio_lower:
        prio_class = "could-have"
        prio_badge_type = "info"

    ac_items_html = []
    for idx, ac in enumerate(raw_ac, start=1):
        given_val = html.escape(str(getattr(ac, "given", "")))
        when_val = html.escape(str(getattr(ac, "when", "")))
        then_val = html.escape(str(getattr(ac, "then", "")))
        ac_items_html.append(
            f'<div class="gherkin-box">'
            f'<div style="font-weight: 600; margin-bottom: 6px; color: #475569;">Kịch bản #{idx}:</div>'
            f'<div class="gherkin-line">'
            f'<span class="gherkin-token token-given">GIVEN</span>'
            f"<span>{given_val}</span>"
            f"</div>"
            f'<div class="gherkin-line">'
            f'<span class="gherkin-token token-when">WHEN</span>'
            f"<span>{when_val}</span>"
            f"</div>"
            f'<div class="gherkin-line">'
            f'<span class="gherkin-token token-then">THEN</span>'
            f"<span>{then_val}</span>"
            f"</div>"
            f"</div>"
        )

    all_ac = "".join(ac_items_html)

    card_html = (
        f'<div class="story-card {prio_class}">'
        f'<div class="story-header">'
        f'<span class="story-req-id">📌 {req_id}</span>'
        f'<span class="bento-badge {prio_badge_type}">⭐ {safe_priority}</span>'
        f"</div>"
        f'<h4 class="story-title">{safe_title}</h4>'
        f'<div class="story-narrative">"{safe_user_story}"</div>'
        f"{all_ac}"
        f"</div>"
    )
    render_clean_html(card_html)
