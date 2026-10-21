"""Enterprise UI Theme and Design Tokens for BA & System Architect Copilot.

Based on UI/UX Pro Max Design Intelligence (Tech & SaaS -> Developer Tool / IDE & B2B Service).
"""

from typing import List, Dict, Any, Optional
import streamlit as st


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
           3. TOP NAVIGATION BANNER & WORKFLOW STEPPER
           ===================================================================== */
        .workbench-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: 1px solid #334155;
            border-radius: var(--radius-lg);
            padding: 20px 24px;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
            color: #ffffff;
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
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
        }

        .brand-title {
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            margin: 0;
            line-height: 1.2;
        }

        .brand-subtitle {
            font-size: 13px;
            color: #94a3b8;
            margin: 2px 0 0 0;
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
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: #e2e8f0;
            backdrop-filter: blur(8px);
        }

        .standard-pill.model-pill {
            background: rgba(79, 70, 229, 0.25);
            border-color: rgba(99, 102, 241, 0.5);
            color: #c7d2fe;
        }

        /* Workflow Stepper */
        .workflow-stepper {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .step-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: var(--radius-md);
            font-size: 12px;
            color: #94a3b8;
        }

        .step-item.active {
            background: rgba(79, 70, 229, 0.2);
            border-color: rgba(99, 102, 241, 0.5);
            color: #ffffff;
            font-weight: 600;
        }

        .step-item.completed {
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
        }

        .step-number {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.12);
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
        .bento-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }

        .bento-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 16px 18px;
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 120px;
            transition: all 0.2s ease;
        }

        .bento-card:hover {
            border-color: var(--brand-primary-border);
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }

        .bento-card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .bento-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .bento-badge {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
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
            font-size: 26px;
            font-weight: 800;
            color: var(--text-heading);
            line-height: 1.1;
            margin-bottom: 6px;
            font-feature-settings: "tnum";
        }

        .bento-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 8px;
        }

        .bento-progress-track {
            width: 100%;
            height: 6px;
            background: var(--bg-muted);
            border-radius: 3px;
            overflow: hidden;
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
           5. SIDEBAR & TELEMETRY PANEL
           ===================================================================== */
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid var(--border-subtle) !important;
        }

        .telemetry-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: var(--radius-lg);
            padding: 16px;
            color: #ffffff;
            margin-top: 12px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
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
            margin-bottom: 12px;
        }

        .telemetry-status-badge.hit {
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .telemetry-status-badge.live {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.4);
        }

        .telemetry-metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 12px;
        }

        .telemetry-cell {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: var(--radius-md);
            padding: 8px 10px;
        }

        .telemetry-label {
            font-size: 11px;
            color: #94a3b8;
            margin-bottom: 2px;
        }

        .telemetry-val {
            font-family: var(--font-mono);
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
        }

        .telemetry-token-bar-wrap {
            background: rgba(255, 255, 255, 0.06);
            border-radius: 4px;
            height: 6px;
            overflow: hidden;
            margin: 6px 0;
            display: flex;
        }

        .token-prompt-fill { background: #3b82f6; height: 100%; }
        .token-completion-fill { background: #10b981; height: 100%; }

        .telemetry-hash {
            font-family: var(--font-mono);
            font-size: 11px;
            color: #cbd5e1;
            background: rgba(255, 255, 255, 0.06);
            padding: 3px 6px;
            border-radius: 4px;
            word-break: break-all;
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
            font-weight: 700;
            font-size: 13px;
            color: var(--text-muted);
        }

        .story-title {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-heading);
            margin: 0;
        }

        .story-narrative {
            font-size: 13.5px;
            color: var(--text-body);
            background: var(--bg-muted);
            border-radius: var(--radius-md);
            padding: 10px 14px;
            margin: 10px 0;
            border-left: 3px solid var(--border-strong);
            font-style: italic;
        }

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
            gap: 8px;
            margin-bottom: 4px;
            align-items: flex-start;
        }

        .gherkin-token {
            font-family: var(--font-mono);
            font-weight: 700;
            font-size: 11px;
            padding: 1px 6px;
            border-radius: 4px;
            min-width: 48px;
            text-align: center;
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
    """Hiển thị Header Bar thương hiệu và Workflow Stepper chuẩn Enterprise."""
    step1_class = "completed" if has_result else "active"
    step2_class = "completed" if has_result else ""
    step3_class = "active" if has_result else ""
    step4_class = "active" if has_result else ""

    html = f"""
    <div class="workbench-header">
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
                <span class="standard-pill">📋 IEEE 29148:2018</span>
                <span class="standard-pill">🏛️ BABOK v3</span>
                <span class="standard-pill">🗄️ 3NF Sandbox</span>
            </div>
        </div>
        <div class="workflow-stepper">
            <div class="step-item {step1_class}">
                <span class="step-number">1</span>
                <span>Elicitation Notes</span>
            </div>
            <div class="step-item {step2_class}">
                <span class="step-number">2</span>
                <span>AI Synthesis</span>
            </div>
            <div class="step-item {step3_class}">
                <span class="step-number">3</span>
                <span>Deterministic Audit</span>
            </div>
            <div class="step-item {step4_class}">
                <span class="step-number">4</span>
                <span>Export Bundle</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_bento_card(
    title: str,
    value: str,
    subtitle: str,
    score_pct: Optional[float] = None,
    badge_text: Optional[str] = None,
    badge_type: str = "info",
    icon: Optional[str] = None,
) -> str:
    """Tạo mã HTML cho một thẻ Bento KPI Card."""
    icon_str = f"{icon} " if icon else ""
    badge_html = ""
    if badge_text:
        badge_html = f'<span class="bento-badge {badge_type}">{badge_text}</span>'

    progress_html = ""
    if score_pct is not None:
        capped_pct = max(0, min(100, float(score_pct)))
        color_class = "success" if capped_pct >= 90 else ("warning" if capped_pct >= 75 else "danger")
        progress_html = f"""
        <div class="bento-progress-track">
            <div class="bento-progress-bar {color_class}" style="width: {capped_pct}%;"></div>
        </div>
        """

    return f"""
    <div class="bento-card">
        <div>
            <div class="bento-card-top">
                <span class="bento-title">{icon_str}{title}</span>
                {badge_html}
            </div>
            <div class="bento-value">{value}</div>
            <div class="bento-subtitle">{subtitle}</div>
        </div>
        {progress_html}
    </div>
    """


def render_bento_grid(cards: List[Any]) -> None:
    """Hiển thị lưới Bento KPI Cards bằng HTML nhúng. Hỗ trợ cả danh sách chuỗi HTML hoặc dict tham số."""
    cards_html = []
    for item in cards:
        if isinstance(item, str):
            cards_html.append(item)
        elif isinstance(item, dict):
            cards_html.append(render_bento_card(**item))
    all_cards = "".join(cards_html)
    grid_html = f'<div class="bento-grid">{all_cards}</div>'
    st.markdown(grid_html, unsafe_allow_html=True)


def render_telemetry_widget(telemetry: Any) -> None:
    """Hiển thị widget giám sát LLMOps Telemetry ở Sidebar."""
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

    html = f"""
    <div class="telemetry-card">
        <div class="telemetry-status-badge {status_class}">
            {status_text}
        </div>
        <div class="telemetry-metric-grid">
            <div class="telemetry-cell">
                <div class="telemetry-label">⏱️ Độ trễ (Latency)</div>
                <div class="telemetry-val">{latency_str}</div>
            </div>
            <div class="telemetry-cell">
                <div class="telemetry-label">🔄 Thử lại (Retries)</div>
                <div class="telemetry-val">{retries}</div>
            </div>
        </div>
        <div class="telemetry-label">🪙 Chi phí Ngữ cảnh (Tokens)</div>
        <div class="telemetry-val" style="font-size: 12px; margin-bottom: 4px;">
            {prompt_tokens:,} in / {completion_tokens:,} out <span style="color:#94a3b8;">({total_tokens:,} Tổng)</span>
        </div>
        <div class="telemetry-token-bar-wrap">
            <div class="token-prompt-fill" style="width: {prompt_pct}%;" title="Prompt Tokens"></div>
            <div class="token-completion-fill" style="width: {completion_pct}%;" title="Completion Tokens"></div>
        </div>
        <div style="margin-top: 8px;">
            <div class="telemetry-label">🔑 SHA-256 Hash Khóa đệm:</div>
            <div class="telemetry-hash">{content_hash[:16]}...</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_user_story_card(
    req_or_id: Any,
    title: Optional[str] = None,
    user_story: Optional[str] = None,
    priority: Optional[str] = None,
    acceptance_criteria: Optional[List[Any]] = None,
) -> None:
    """Hiển thị thẻ User Story chuẩn MoSCoW kèm kịch bản Gherkin BDD."""
    if hasattr(req_or_id, "req_id"):
        req_id = req_or_id.req_id
        title = title or getattr(req_or_id, "title", "")
        user_story = user_story or getattr(req_or_id, "user_story", "")
        priority = priority or getattr(req_or_id, "priority", "Medium")
        acceptance_criteria = acceptance_criteria or getattr(req_or_id, "acceptance_criteria", [])
    else:
        req_id = str(req_or_id)
        title = title or ""
        user_story = user_story or ""
        priority = priority or "Medium"
        acceptance_criteria = acceptance_criteria or []

    prio_class = "must-have"
    prio_badge_type = "danger"
    prio_lower = (priority or "medium").lower()
    if "should" in prio_lower or "medium" in prio_lower:
        prio_class = "should-have"
        prio_badge_type = "warning"
    elif "could" in prio_lower or "low" in prio_lower:
        prio_class = "could-have"
        prio_badge_type = "info"

    ac_items_html = []
    for idx, ac in enumerate(acceptance_criteria, start=1):
        given_val = getattr(ac, "given", "")
        when_val = getattr(ac, "when", "")
        then_val = getattr(ac, "then", "")
        ac_items_html.append(f"""
        <div class="gherkin-box">
            <div style="font-weight: 600; margin-bottom: 6px; color: #475569;">Kịch bản #{idx}:</div>
            <div class="gherkin-line">
                <span class="gherkin-token token-given">GIVEN</span>
                <span>{given_val}</span>
            </div>
            <div class="gherkin-line">
                <span class="gherkin-token token-when">WHEN</span>
                <span>{when_val}</span>
            </div>
            <div class="gherkin-line">
                <span class="gherkin-token token-then">THEN</span>
                <span>{then_val}</span>
            </div>
        </div>
        """)

    all_ac = "".join(ac_items_html)

    card_html = f"""
    <div class="story-card {prio_class}">
        <div class="story-header">
            <span class="story-req-id">📌 {req_id}</span>
            <span class="bento-badge {prio_badge_type}">⭐ {priority}</span>
        </div>
        <h4 class="story-title">{title}</h4>
        <div class="story-narrative">"{user_story}"</div>
        {all_ac}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
