"""Streamlit Web Application: AI Business Analyst & System Architect Copilot."""

import os
import re
import json
from typing import Optional
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env nếu có
load_dotenv()

from src.models.srs_schema import SRSDocument
from src.services.ai_generator import (
    generate_srs_from_notes,
    generate_srs_with_telemetry,
)
from src.services.telemetry_cache import default_srs_cache, TelemetryMetrics
from src.services.exporter import (
    create_project_bundle_zip,
    generate_markdown_report,
    generate_rtm_csv_bytes,
)
from src.data.sample_inputs import SAMPLE_SCENARIOS
from src.validators.syntax_validator import clean_and_validate_mermaid, validate_sql_ddl
from src.validators.db_sandbox import execute_and_audit_ddl
from src.validators.requirements_linter import evaluate_srs_deterministically
from src.validators.consistency_checker import (
    audit_cross_model_consistency,
    auto_sync_rtm_and_erd_with_ddl,
)
from src.ui.theme import (
    apply_custom_theme,
    render_header_banner,
    render_bento_grid,
    render_telemetry_widget,
    render_user_story_card,
)

# Tương thích ngược với các module và test
export_srs_markdown = generate_markdown_report

# Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="AI BA & System Architect Copilot",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Áp dụng bộ quy tắc thiết kế chuẩn Enterprise SaaS từ UI/UX Pro Max
apply_custom_theme()

# Tự động dọn dẹp session_state nếu đối tượng SRSDocument từ phiên cũ thiếu thuộc tính mới
for ss_key in ["srs_result", "doc"]:
    if ss_key in st.session_state and st.session_state[ss_key] is not None:
        if not hasattr(st.session_state[ss_key], "state_diagram_mermaid"):
            st.session_state.pop(ss_key, None)


def render_mermaid(mermaid_code: str, height: int = 560, diagram_type: str = "") -> None:
    """Nhúng thư viện Mermaid.js từ CDN và render sơ đồ tương tác (Interactive SVG Canvas)
    với thanh công cụ nổi (Zoom In, Zoom Out, Reset, Download SVG), hỗ trợ kéo rê (Pan)
    và phóng to thu nhỏ (Zoom), kết hợp cơ chế Lazy Visibility Rendering để tránh lỗi khi tab đang ẩn.
    """
    try:
        clean_code = clean_and_validate_mermaid(mermaid_code, diagram_type=diagram_type)
    except Exception:
        clean_code = mermaid_code.strip()

    code_json = json.dumps(clean_code)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            * {{
                box-sizing: border-box;
            }}
            body {{
                margin: 0;
                padding: 0;
                background-color: #f8fafc;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                overflow: hidden;
                width: 100vw;
                height: 100vh;
            }}
            #viewport {{
                position: relative;
                width: 100%;
                height: 100%;
                overflow: hidden;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                cursor: grab;
                user-select: none;
            }}
            #viewport.dragging {{
                cursor: grabbing;
            }}
            #canvas-wrapper {{
                position: absolute;
                top: 0;
                left: 0;
                transform-origin: 0 0;
                display: inline-block;
                padding: 24px;
            }}
            #mermaid-container {{
                display: inline-block;
            }}
            #mermaid-container svg {{
                display: block;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
                border-radius: 8px;
                padding: 12px;
                background: #ffffff;
            }}
            #toolbar {{
                position: absolute;
                top: 12px;
                right: 12px;
                z-index: 100;
                display: flex;
                align-items: center;
                gap: 6px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(6px);
                padding: 4px 8px;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
            }}
            .tool-btn {{
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                color: #1e293b;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.15s ease;
                user-select: none;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            .tool-btn:hover {{
                background: #e2e8f0;
                border-color: #94a3b8;
            }}
            .tool-btn:active {{
                background: #cbd5e1;
            }}
            #zoom-indicator {{
                font-size: 12px;
                font-weight: 600;
                color: #475569;
                min-width: 42px;
                text-align: center;
            }}
            .mermaid-error {{
                color: #b91c1c;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 16px;
                font-family: monospace;
                font-size: 13px;
                white-space: pre-wrap;
                margin: 20px;
            }}
        </style>
    </head>
    <body>
        <div id="viewport">
            <div id="toolbar">
                <button class="tool-btn" id="btn-zoom-in" title="Phóng to (Ctrl + Cuộn chuột)">➕</button>
                <button class="tool-btn" id="btn-zoom-out" title="Thu nhỏ (Ctrl + Cuộn chuột)">➖</button>
                <span id="zoom-indicator">100%</span>
                <button class="tool-btn" id="btn-reset" title="Đặt lại góc nhìn (Reset 100%)">🔄 Reset</button>
                <button class="tool-btn" id="btn-download" title="Tải ảnh vector SVG chất lượng cao">⬇️ Tải SVG</button>
            </div>
            <div id="canvas-wrapper">
                <div id="mermaid-container">
                    <div style="color: #64748b; font-size: 14px; padding: 20px;">Đang tải sơ đồ Mermaid...</div>
                </div>
            </div>
        </div>

        <script>
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose'
            }});

            let scale = 1.0;
            let pointX = 0;
            let pointY = 0;
            let isPanning = false;
            let startX = 0;
            let startY = 0;
            let rendered = false;
            let resizeObserver = null;
            let intersectionObserver = null;

            function updateTransform() {{
                const wrapper = document.getElementById('canvas-wrapper');
                if (!wrapper) return;
                wrapper.style.transform = 'translate(' + pointX + 'px, ' + pointY + 'px) scale(' + scale + ')';
                const indicator = document.getElementById('zoom-indicator');
                if (indicator) {{
                    indicator.innerText = Math.round(scale * 100) + '%';
                }}
            }}

            function zoom(factor, clientX, clientY) {{
                const viewport = document.getElementById('viewport');
                const rect = viewport.getBoundingClientRect();
                const cx = (clientX !== undefined) ? (clientX - rect.left) : (rect.width / 2);
                const cy = (clientY !== undefined) ? (clientY - rect.top) : (rect.height / 2);

                const oldScale = scale;
                let newScale = scale * factor;
                if (newScale < 0.2) newScale = 0.2;
                if (newScale > 5.0) newScale = 5.0;

                pointX = cx - (cx - pointX) * (newScale / oldScale);
                pointY = cy - (cy - pointY) * (newScale / oldScale);
                scale = newScale;
                updateTransform();
            }}

            function resetView() {{
                scale = 1.0;
                const viewport = document.getElementById('viewport');
                const container = document.getElementById('mermaid-container');
                if (viewport && container && container.offsetWidth > 0) {{
                    pointX = Math.max(16, (viewport.clientWidth - container.offsetWidth) / 2);
                    pointY = 20;
                }} else {{
                    pointX = 20;
                    pointY = 20;
                }}
                updateTransform();
            }}

            function downloadSVG() {{
                const container = document.getElementById('mermaid-container');
                const svgElem = container ? container.querySelector('svg') : null;
                if (!svgElem) {{
                    alert("Chưa có sơ đồ SVG để tải về.");
                    return;
                }}
                const svgData = new XMLSerializer().serializeToString(svgElem);
                const blob = new Blob([svgData], {{ type: 'image/svg+xml;charset=utf-8' }});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mermaid_diagram_' + Date.now() + '.svg';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}

            async function renderDiagram() {{
                const container = document.getElementById('mermaid-container');
                const rawCode = {code_json};
                const renderId = 'mermaid_svg_' + Math.random().toString(36).substring(2, 9);
                try {{
                    const {{ svg }} = await mermaid.render(renderId, rawCode);
                    container.innerHTML = svg;
                    setTimeout(resetView, 60);
                }} catch (err) {{
                    console.error("Mermaid Render Error:", err);
                    container.innerHTML = '<div class="mermaid-error"><strong>⚠️ Lỗi hiển thị Mermaid:</strong><br>' +
                        (err.message || err) + '</div>';
                }}
            }}

            function cleanupObservers() {{
                if (resizeObserver) {{
                    resizeObserver.disconnect();
                    resizeObserver = null;
                }}
                if (intersectionObserver) {{
                    intersectionObserver.disconnect();
                    intersectionObserver = null;
                }}
            }}

            function checkAndRender() {{
                if (rendered) return;
                const viewport = document.getElementById('viewport');
                const container = document.getElementById('mermaid-container');
                if (!viewport || !container) return;

                if (document.body.offsetWidth > 0 && viewport.offsetWidth > 0) {{
                    rendered = true;
                    cleanupObservers();
                    renderDiagram();
                }}
            }}

            // Gắn sự kiện Pan kéo thả chuột
            const viewport = document.getElementById('viewport');
            viewport.addEventListener('mousedown', (e) => {{
                if (e.target.closest('#toolbar')) return;
                isPanning = true;
                startX = e.clientX - pointX;
                startY = e.clientY - pointY;
                viewport.classList.add('dragging');
            }});

            window.addEventListener('mousemove', (e) => {{
                if (!isPanning) return;
                pointX = e.clientX - startX;
                pointY = e.clientY - startY;
                updateTransform();
            }});

            window.addEventListener('mouseup', () => {{
                if (isPanning) {{
                    isPanning = false;
                    viewport.classList.remove('dragging');
                }}
            }});

            // Phóng to thu nhỏ bằng con lăn chuột (Wheel Zoom / Ctrl + Wheel)
            viewport.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const factor = e.deltaY < 0 ? 1.15 : 0.87;
                zoom(factor, e.clientX, e.clientY);
            }}, {{ passive: false }});

            // Gắn sự kiện thanh công cụ
            document.getElementById('btn-zoom-in').addEventListener('click', (e) => {{
                e.stopPropagation();
                zoom(1.2);
            }});
            document.getElementById('btn-zoom-out').addEventListener('click', (e) => {{
                e.stopPropagation();
                zoom(1 / 1.2);
            }});
            document.getElementById('btn-reset').addEventListener('click', (e) => {{
                e.stopPropagation();
                resetView();
            }});
            document.getElementById('btn-download').addEventListener('click', (e) => {{
                e.stopPropagation();
                downloadSVG();
            }});

            // 1. Nếu đang ở Tab hiển thị sẵn -> gọi render ngay
            if (document.body.offsetWidth > 0 && viewport && viewport.offsetWidth > 0) {{
                rendered = true;
                renderDiagram();
            }} else {{
                // 2. Nếu nằm trong Tab ẩn của Streamlit -> theo dõi khi Tab được click mở
                if (window.ResizeObserver) {{
                    resizeObserver = new ResizeObserver(() => {{
                        checkAndRender();
                    }});
                    resizeObserver.observe(document.body);
                    if (viewport) {{
                        resizeObserver.observe(viewport);
                    }}
                }}

                if (window.IntersectionObserver && viewport) {{
                    intersectionObserver = new IntersectionObserver((entries) => {{
                        for (const entry of entries) {{
                            if (entry.isIntersecting || entry.intersectionRatio > 0) {{
                                checkAndRender();
                            }}
                        }}
                    }});
                    intersectionObserver.observe(viewport);
                }}

                window.addEventListener('resize', checkAndRender);
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=False)

# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/blueprint.png", width=64)
    st.markdown("### 🛠️ Trung tâm Điều khiển")
    st.caption("AI Principal BA & Solution Architect Workbench")

    # Đóng gói API Key Card
    with st.container(border=True):
        st.markdown("##### 🔑 Cấu hình Gemini API")
        env_key = os.getenv("GEMINI_API_KEY", "")
        api_key_input = st.text_input(
            "Google Gemini API Key:",
            value=env_key,
            type="password",
            placeholder="AIzaSy...",
            help="Lấy API Key miễn phí tại https://aistudio.google.com/",
            label_visibility="collapsed",
        )
        api_key = api_key_input.strip() if api_key_input else env_key

        if api_key:
            st.success("Đã kết nối API Key", icon="🔑")
        else:
            st.warning("Chưa cấu hình GEMINI_API_KEY", icon="⚡")

    # Đóng gói Kịch bản Mẫu Khảo sát
    with st.container(border=True):
        st.markdown("##### 📚 Kịch bản Mẫu Khảo sát")
        scenario_options = {
            "custom": "-- Tự nhập ghi chú họp thực tế --",
            "cinema_booking": "🎬 1. Rạp chiếu phim CineMax (Khóa ghế, Đặt vé)",
            "bus_logistics": "🚌 2. Xe khách Phương Nam (Lịch chạy, Gửi hàng)",
            "warehouse_inventory": "📦 3. Kho thông minh LogiTech (WMS, FIFO, Tồn kho)",
        }

        selected_scenario = st.selectbox(
            "Chọn kịch bản nạp nhanh:",
            options=list(scenario_options.keys()),
            format_func=lambda k: scenario_options[k],
            label_visibility="collapsed",
        )

        if selected_scenario != "custom" and selected_scenario in SAMPLE_SCENARIOS:
            sample_data = SAMPLE_SCENARIOS[selected_scenario]
            if st.button("📥 Nạp kịch bản này vào khung nhập", use_container_width=True):
                st.session_state["raw_notes_input"] = sample_data["meeting_notes"]
                st.rerun()

    # Đóng gói Tối ưu Hiệu năng LLMOps
    with st.container(border=True):
        st.markdown("##### ⚡ Tối ưu Hiệu năng (LLMOps)")
        force_cache_refresh = st.checkbox(
            "⚡ Bỏ qua bộ nhớ đệm (Force Live Call)",
            value=False,
            help="Bắt buộc gọi trực tiếp Gemini API mà không sử dụng kết quả trong RAM cache",
        )
        if st.button("🗑️ Xóa Bộ nhớ đệm SHA-256 Cache", use_container_width=True):
            default_srs_cache.clear()
            st.toast("✅ Đã xóa toàn bộ bộ nhớ đệm SHA-256 Cache!", icon="🗑️")

    # Bảng Giám sát Chỉ số Vận hành LLMOps Telemetry Panel
    telemetry: Optional[TelemetryMetrics] = st.session_state.get("telemetry_metrics")
    if telemetry:
        st.markdown("##### 📡 Giám sát Chỉ số Vận hành LLMOps")
        render_telemetry_widget(telemetry)

    st.markdown("""
    <div style="font-size: 11px; color: #64748b; margin-top: 16px; line-height: 1.6; border-top: 1px solid #e2e8f0; padding-top: 12px;">
        <strong>Hệ quy chiếu Tiêu chuẩn:</strong><br>
        • <b>IEEE 29148:</b> Requirements Engineering<br>
        • <b>BABOK v3:</b> Requirements Traceability Matrix<br>
        • <b>Gherkin BDD:</b> Given - When - Then<br>
        • <b>3NF Sandbox:</b> Boyce-Codd Normal Form<br>
        • <b>Core LLM:</b> <code>gemini-3.8-flash</code>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# MAIN CONTENT AREA
# -------------------------------------------------------------
# Khởi tạo session state cho input và output
if "raw_notes_input" not in st.session_state:
    st.session_state["raw_notes_input"] = SAMPLE_SCENARIOS["cinema_booking"]["meeting_notes"]

if "srs_result" not in st.session_state:
    st.session_state["srs_result"] = None
else:
    cached_doc = st.session_state.get("srs_result")
    if cached_doc is not None and not hasattr(cached_doc, "state_diagram_mermaid"):
        st.session_state["srs_result"] = None

doc_preview: Optional[SRSDocument] = st.session_state.get("srs_result")

# Thanh Tiêu đề Top Navigation Banner với Workflow Stepper
render_header_banner(has_result=bool(doc_preview))

# Khung nhập Biên bản họp thông minh (Smart Expander: tự mở khi chưa có kết quả, tự thu gọn khi đã có SRS)
with st.expander("📝 Biên bản Ghi chú Họp Khách hàng (Raw Meeting Notes Input)", expanded=(doc_preview is None)):
    st.caption("Dán biên bản khảo sát yêu cầu nghiệp vụ, câu hỏi phỏng vấn stakeholder hoặc quy trình vận hành thô:")
    meeting_notes_text = st.text_area(
        "Nội dung Biên bản Ghi chú Họp Khách hàng (Raw Meeting Notes):",
        value=st.session_state["raw_notes_input"],
        height=220,
        placeholder="Dán nội dung thảo luận với khách hàng, yêu cầu nghiệp vụ, quy trình hoạt động...",
        label_visibility="collapsed",
    )

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        generate_clicked = st.button(
            "🚀 Phân tích & Sinh Đặc tả Hệ thống",
            type="primary",
            use_container_width=True,
        )

    with col_info:
        if not api_key:
            st.info("💡 Vui lòng cấu hình `GEMINI_API_KEY` ở thanh bên trái để thực hiện phân tích.")

if generate_clicked:
    if not api_key:
        st.error("Lỗi: Bạn cần cung cấp Gemini API Key để thực hiện.")
    elif not meeting_notes_text.strip():
        st.error("Lỗi: Vui lòng nhập nội dung ghi chú họp trước khi phân tích.")
    else:
        with st.spinner("🤖 AI Principal BA & Enterprise Architect đang phân tích nghiệp vụ, chuẩn hóa 3NF và sinh sơ đồ..."):
            try:
                result_doc, telemetry_metrics = generate_srs_with_telemetry(
                    meeting_notes_text,
                    api_key,
                    force_refresh=force_cache_refresh,
                )
                st.session_state["srs_result"] = result_doc
                st.session_state["telemetry_metrics"] = telemetry_metrics
                # Dọn dẹp các key widget live edit để đồng bộ kết quả mới
                for edit_k in [
                    "edit_seq_mermaid",
                    "edit_state_mermaid",
                    "live_workbench_erd",
                    "live_workbench_sql",
                ]:
                    st.session_state.pop(edit_k, None)

                if telemetry_metrics.cache_hit:
                    st.toast(
                        f"⚡ Tải từ Bộ nhớ đệm SHA-256 trong {telemetry_metrics.latency_ms:.1f}ms (Tiết kiệm 100% token)!",
                        icon="⚡",
                    )
                else:
                    st.toast(
                        f"🎉 Đã sinh thành công Đặc tả Hệ thống qua Gemini API ({telemetry_metrics.total_tokens} tokens)!",
                        icon="✅",
                    )
                st.rerun()
            except Exception as e:
                st.error(f"❌ Quá trình phân tích gặp sự cố: {str(e)}")

# -------------------------------------------------------------
# HIỂN THỊ KẾT QUẢ TRÊN 4 TABS
# -------------------------------------------------------------
doc: SRSDocument = st.session_state.get("srs_result")
if doc is not None and not hasattr(doc, "state_diagram_mermaid"):
    st.session_state["srs_result"] = None
    doc = None

if doc:
    st.markdown("---")
    st.subheader(f"📑 Dự án: {doc.project_title}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Tab 1: Đặc tả Yêu cầu (SRS & User Stories)",
        "🔄 Tab 2: Mô hình Động UML (Sequence & State Machine)",
        "🗄️ Tab 3: Thiết kế CSDL (ERD 3NF & SQL DDL)",
        "📥 Tab 4: Xuất Tài liệu (Export Markdown)",
    ])

    # ---------------- TAB 1: SRS & USER STORIES ----------------
    with tab1:
        # Thẻ chỉ số chất lượng & kiểm toán (Quality Audit Metrics)
        quality_audit = getattr(doc, "quality_audit", None)
        ieee_score = getattr(quality_audit, "ieee_compliance_score", 95) if quality_audit else 95
        invest_score = getattr(quality_audit, "invest_score", 90) if quality_audit else 90
        fr_count = len(doc.functional_requirements)

        # Chạy Bộ Kiểm định Cú pháp Xác định (Deterministic Static Linter)
        linter_result = evaluate_srs_deterministically(doc)
        det_ieee_score = linter_result["deterministic_ieee_score"]
        det_invest_score = linter_result["deterministic_invest_score"]
        rtm_coverage_pct = linter_result["rtm_coverage_pct"]
        lint_warnings = linter_result["lint_warnings"]

        st.markdown("##### 📊 Chỉ số Đánh giá Chất lượng Đặc tả & Độ phủ (Bento KPI Grid)")

        # Render Bento Grid KPI Cards
        bento_cards = [
            {
                "title": "Điểm Chuẩn IEEE 29148",
                "value": f"{det_ieee_score}/100",
                "subtitle": f"Deterministic Linter (AI: {ieee_score})",
                "score_pct": float(det_ieee_score),
                "badge_text": "IEEE 29148" if det_ieee_score >= 80 else "Cần Chuẩn Hóa",
                "badge_type": "success" if det_ieee_score >= 80 else "warning",
                "icon": "📐",
            },
            {
                "title": "Điểm User Story INVEST",
                "value": f"{det_invest_score}/100",
                "subtitle": f"Rule-based (AI: {invest_score})",
                "score_pct": float(det_invest_score),
                "badge_text": "INVEST Criteria" if det_invest_score >= 80 else "Cần Tách Nhỏ",
                "badge_type": "success" if det_invest_score >= 80 else "warning",
                "icon": "🎯",
            },
            {
                "title": "Độ phủ Truy vết RTM",
                "value": f"{rtm_coverage_pct}%",
                "subtitle": "BABOK v3 Traceability",
                "score_pct": float(rtm_coverage_pct),
                "badge_text": "100% Hoàn chỉnh" if rtm_coverage_pct == 100.0 else f"Thiếu {100.0 - rtm_coverage_pct:.1f}%",
                "badge_type": "success" if rtm_coverage_pct == 100.0 else "danger",
                "icon": "🔗",
            },
            {
                "title": "Yêu cầu Chức năng",
                "value": f"{fr_count} Yêu cầu",
                "subtitle": "MoSCoW & BDD Gherkin",
                "score_pct": min(100.0, fr_count * 20.0),
                "badge_text": "Cấu trúc hóa",
                "badge_type": "info",
                "icon": "📋",
            },
        ]
        render_bento_grid(bento_cards)

        # Báo cáo Kiểm toán Cú pháp & Ngữ nghĩa
        if lint_warnings:
            with st.expander("🔍 Báo cáo Kiểm toán Tự động Cú pháp Yêu cầu (Automated Static Linter Report)", expanded=True):
                st.warning(f"⚠️ Phát hiện {len(lint_warnings)} cảnh báo chất lượng cần chuẩn hóa cú pháp theo chuẩn IEEE 29148 & INVEST:")
                for w_idx, warning_text in enumerate(lint_warnings, start=1):
                    st.markdown(f"**{w_idx}.** {warning_text}")
        else:
            st.success("100% Yêu cầu vượt qua bài kiểm tra từ ngữ mơ hồ và định lượng SLA chuẩn IEEE 29148.")


        # Cảnh báo Điểm Mơ hồ & Câu hỏi Phỏng vấn lại Khách hàng
        if quality_audit and getattr(quality_audit, "clarification_questions", []):
            st.markdown("#### ❓ Cảnh báo Điểm Mơ hồ & Câu hỏi Phỏng vấn lại Khách hàng (Elicitation Follow-up Questions)")
            with st.container(border=True):
                st.warning("⚠️ **Phân tích Rủi ro & Điểm Mơ hồ Nghiệp vụ:** Dựa trên biên bản họp thô, AI Business Analyst phát hiện các khoảng trống thông tin cần phỏng vấn xác nhận lại với Stakeholders để tránh rủi ro phát sinh phạm vi (Scope Creep):")
                for q_idx, question in enumerate(quality_audit.clarification_questions, start=1):
                    st.markdown(f"**{q_idx}.** {question}")

        st.markdown("#### 🎯 Mục tiêu Kinh doanh (Business Objective)")
        st.info(doc.business_objective)

        st.markdown("#### 👥 Danh sách Tác nhân Hệ thống (Actors)")
        actors_cols = st.columns(len(doc.actors) if doc.actors else 1)
        for idx, actor in enumerate(doc.actors):
            with actors_cols[idx % len(actors_cols)]:
                st.success(f"👤 **{actor}**")

        st.markdown("#### 📝 Danh mục Yêu cầu Chức năng (Functional Requirements & MoSCoW Cards)")
        st.caption("Mỗi yêu cầu được gắn nhãn ưu tiên MoSCoW và đóng khung kịch bản nghiệm thu Given-When-Then chuẩn Gherkin BDD:")
        for fr in doc.functional_requirements:
            render_user_story_card(fr)

        st.markdown("#### 🛡️ Yêu cầu Phi Chức năng (Non-Functional Requirements)")
        nfr_data = [
            {
                "Phân loại": nfr.category,
                "Mô tả yêu cầu (IEEE 29148)": nfr.description,
                "Chỉ số nghiệm thu (Metric / SLA)": nfr.metric,
            }
            for nfr in doc.non_functional_requirements
        ]
        st.table(nfr_data)

        # Ma trận Truy vết Yêu cầu (Requirements Traceability Matrix - RTM)
        traceability_matrix = getattr(doc, "traceability_matrix", [])
        if traceability_matrix:
            st.markdown("#### 🔗 Ma trận Truy vết Yêu cầu (Requirements Traceability Matrix - RTM)")
            st.caption("Chuỗi giá trị truy vết theo chuẩn BABOK v3: Mã YC ➔ Tính năng ➔ Quy tắc Nghiệp vụ ➔ Bảng CSDL Liên quan ➔ Kịch bản Kiểm thử Nghiệm thu.")
            rtm_table = [
                {
                    "Mã YC": item.req_id,
                    "Tên Tính năng": item.feature_name,
                    "Quy tắc Nghiệp vụ (Business Rule)": item.business_rule,
                    "Bảng CSDL Liên quan": ", ".join(item.related_tables) if isinstance(item.related_tables, list) else str(item.related_tables),
                    "Kịch bản Kiểm thử Nghiệm thu": item.test_scenario_summary,
                }
                for item in traceability_matrix
            ]
            st.dataframe(rtm_table, use_container_width=True, hide_index=True)

        # Kiểm định Tính Nhất quán Liên Mô hình (Cross-Artifact Consistency: RTM ↔ ERD ↔ SQL)
        st.divider()
        st.markdown("#### 🔗 Kiểm định Tính Nhất quán Liên Mô hình (Cross-Artifact Consistency: RTM ↔ ERD ↔ SQL)")
        st.caption("Đối chiếu tập hợp thực thể trên cả 3 tầng: Ma trận RTM (Tab 1), Sơ đồ ERD 3NF (Tab 3), và Kịch bản SQL DDL (Tab 3) bằng lý thuyết Đại số Tập hợp.")

        consistency_audit = audit_cross_model_consistency(doc)
        consistency_cards = [
            {
                "title": "Đồng bộ Liên Mô hình",
                "value": f"{consistency_audit['consistency_score']}%",
                "subtitle": "Đại số Tập hợp RTM ↔ ERD ↔ DDL",
                "score_pct": float(consistency_audit['consistency_score']),
                "badge_text": "100% Đồng nhất" if consistency_audit['consistency_score'] == 100 else f"Lệch {100 - consistency_audit['consistency_score']}%",
                "badge_type": "success" if consistency_audit['consistency_score'] == 100 else "danger",
                "icon": "🔄",
            },
            {
                "title": "Tập Bảng RTM (T_RTM)",
                "value": f"{len(consistency_audit['rtm_tables'])} Bảng",
                "subtitle": "Traceability Scope",
                "score_pct": min(100.0, len(consistency_audit['rtm_tables']) * 20.0),
                "badge_text": "BABOK v3",
                "badge_type": "info",
                "icon": "📋",
            },
            {
                "title": "Thực thể ERD (T_ERD)",
                "value": f"{len(consistency_audit['erd_entities'])} Thực thể",
                "subtitle": "Mermaid 3NF Diagram",
                "score_pct": min(100.0, len(consistency_audit['erd_entities']) * 20.0),
                "badge_text": "Logical Model",
                "badge_type": "info",
                "icon": "🗄️",
            },
            {
                "title": "Bảng Vật lý (T_DDL)",
                "value": f"{len(consistency_audit['ddl_tables'])} Bảng",
                "subtitle": "SQLite RAM Schema",
                "score_pct": min(100.0, len(consistency_audit['ddl_tables']) * 20.0),
                "badge_text": "Physical DDL",
                "badge_type": "info",
                "icon": "💾",
            },
        ]
        render_bento_grid(consistency_cards)

        if not consistency_audit["is_fully_synced"]:
            phantom = consistency_audit.get("phantom_tables_in_rtm", [])
            orphan = consistency_audit.get("orphan_tables_in_ddl", [])
            missing_erd = consistency_audit.get("missing_in_erd", [])

            warning_msgs = []
            if phantom:
                warning_msgs.append(f"**Bảng có trong RTM nhưng thiếu trong SQL DDL (Phantom Tables):** `{', '.join(phantom)}`")
            if orphan:
                warning_msgs.append(f"**Bảng có trong SQL DDL nhưng chưa gán trong RTM (Orphan Tables):** `{', '.join(orphan)}`")
            if missing_erd:
                warning_msgs.append(f"**Bảng trong SQL DDL chưa được vẽ trong ERD (Missing in ERD):** `{', '.join(missing_erd)}`")

            st.warning(
                "⚠️ **Phát hiện sự không nhất quán giữa các tầng đặc tả:**\n\n" +
                "\n\n".join(f"- {msg}" for msg in warning_msgs)
            )

            if st.button("🔄 Tự động Đồng bộ Hóa Tên Bảng Liên Mô hình (Auto-Sync Artifacts)", key="btn_sync_artifacts_tab1", type="primary"):
                synced_doc = auto_sync_rtm_and_erd_with_ddl(doc)
                st.session_state["srs_result"] = synced_doc
                st.session_state["live_workbench_erd"] = synced_doc.er_diagram_mermaid
                st.toast("✅ Đã tự động đồng bộ hóa bảng giữa RTM, ERD và SQL DDL!", icon="🔄")
                st.rerun()
        else:
            st.success("✅ **100% Nhất quán Liên Mô hình:** Tất cả các bảng trong Ma trận RTM, Sơ đồ ERD và Kịch bản SQL DDL hoàn toàn đồng nhất!")

    # ---------------- TAB 2: UML DYNAMIC MODELS (SEQUENCE & STATE MACHINE) ----------------
    with tab2:
        st.markdown("#### 🔄 Sơ đồ Tuần tự Nghiệp vụ Trọng tâm (UML Sequence Diagram)")
        st.caption("Minh họa luồng tương tác giữa các tác nhân và thành phần hệ thống theo thời gian.")

        render_mermaid(doc.sequence_diagram_mermaid, height=560, diagram_type="sequenceDiagram")

        with st.expander("🛠️ Xem & Tinh chỉnh Trực tiếp Mã nguồn Mermaid Sequence Diagram (Live Edit)"):
            new_seq_code = st.text_area(
                "Chỉnh sửa mã Mermaid Sequence Diagram:",
                value=doc.sequence_diagram_mermaid,
                height=220,
                key="edit_seq_mermaid",
            )
            if st.button("🔄 Cập nhật Sơ đồ Sequence", key="btn_update_seq"):
                try:
                    cleaned_seq = clean_and_validate_mermaid(new_seq_code, diagram_type="sequenceDiagram")
                    doc.sequence_diagram_mermaid = cleaned_seq
                except Exception:
                    doc.sequence_diagram_mermaid = new_seq_code
                st.session_state["srs_result"] = doc
                st.toast("✅ Đã cập nhật Sơ đồ Tuần tự!", icon="🔄")
                st.rerun()

        state_diagram = getattr(doc, "state_diagram_mermaid", "")
        state_entity = getattr(doc, "state_machine_entity", "")
        if state_diagram:
            st.divider()
            entity_label = f": {state_entity}" if state_entity else ""
            st.markdown(f"#### 🚦 Sơ đồ Máy Trạng thái Thực thể Cốt lõi (UML State Machine Diagram){entity_label}")
            st.caption("Mô hình hóa vòng đời trạng thái, sự kiện kích hoạt và điều kiện rẽ nhánh của thực thể trung tâm.")

            render_mermaid(state_diagram, height=560, diagram_type="stateDiagram-v2")

            with st.expander("🛠️ Xem & Tinh chỉnh Trực tiếp Mã nguồn Mermaid State Machine Diagram (Live Edit)"):
                new_state_code = st.text_area(
                    "Chỉnh sửa mã Mermaid State Machine Diagram:",
                    value=state_diagram,
                    height=220,
                    key="edit_state_mermaid",
                )
                if st.button("🔄 Cập nhật Sơ đồ State Machine", key="btn_update_state"):
                    try:
                        cleaned_state = clean_and_validate_mermaid(new_state_code, diagram_type="stateDiagram-v2")
                        doc.state_diagram_mermaid = cleaned_state
                    except Exception:
                        doc.state_diagram_mermaid = new_state_code
                    st.session_state["srs_result"] = doc
                    st.toast("✅ Đã cập nhật Sơ đồ Máy Trạng thái!", icon="🔄")
                    st.rerun()

    # ---------------- TAB 3: ERD 3NF & SQL DDL ----------------
    with tab3:
        with st.expander("🛠️ Chế độ Tinh chỉnh Kiến trúc CSDL (DBA Live Workbench)", expanded=False):
            st.caption("Cho phép Kỹ sư CSDL / Solution Architect chỉnh sửa trực tiếp sơ đồ ERD hoặc thêm/sửa bảng, cột, khóa ngoại trong kịch bản SQL DDL để kiểm định lại tức thì.")
            workbench_col1, workbench_col2 = st.columns(2, gap="medium")
            with workbench_col1:
                live_erd_input = st.text_area(
                    "Chỉnh sửa Mermaid ERD (3NF):",
                    value=doc.er_diagram_mermaid,
                    height=240,
                    key="live_workbench_erd",
                )
            with workbench_col2:
                live_sql_input = st.text_area(
                    "Chỉnh sửa Kịch bản SQL DDL (PostgreSQL / ANSI):",
                    value=doc.sql_ddl_script,
                    height=240,
                    key="live_workbench_sql",
                )

            if st.button("🚀 Áp dụng & Kiểm định lại CSDL", type="primary", key="btn_apply_db_live"):
                try:
                    cleaned_erd = clean_and_validate_mermaid(live_erd_input, diagram_type="erDiagram")
                    doc.er_diagram_mermaid = cleaned_erd
                except Exception:
                    doc.er_diagram_mermaid = live_erd_input

                doc.sql_ddl_script = live_sql_input
                st.session_state["srs_result"] = doc
                st.toast("⚡ Đã cập nhật CSDL và chạy kiểm toán Sandbox thành công!", icon="✅")
                st.rerun()

        col_erd, col_sql = st.columns([1, 1], gap="medium")

        with col_erd:
            st.markdown("#### 🗄️ Sơ đồ Thực thể Quan hệ Chuẩn 3NF")
            st.caption("Triệt tiêu phụ thuộc từng phần (2NF) và phụ thuộc bắc cầu (3NF).")
            render_mermaid(doc.er_diagram_mermaid, height=560, diagram_type="erDiagram")

            with st.expander("📄 Xem mã nguồn Mermaid ERD"):
                st.code(doc.er_diagram_mermaid, language="mermaid")

            quality_audit = getattr(doc, "quality_audit", None)
            if quality_audit and getattr(quality_audit, "third_nf_justification", ""):
                with st.expander("🏛️ Giải trình Thiết kế CSDL Đạt Chuẩn 3NF (3NF Justification)", expanded=False):
                    st.info(quality_audit.third_nf_justification)

        with col_sql:
            st.markdown("#### 💾 Kịch bản Khởi tạo CSDL (SQL DDL)")

            # Kiểm định cú pháp SQL DDL bằng sqlglot
            is_sql_valid, sql_validation_msg = validate_sql_ddl(doc.sql_ddl_script)
            if is_sql_valid:
                st.success(f"✅ {sql_validation_msg} (Kiểm định bởi `sqlglot AST Parser`)")
            else:
                st.warning(f"⚠️ Cảnh báo kiểm định SQL: {sql_validation_msg}")

            st.code(doc.sql_ddl_script, language="sql")

        # Báo cáo Kiểm toán Thực thi Vật lý CSDL (In-Memory DB Sandbox Audit)
        st.divider()
        st.markdown("#### 🧪 Báo cáo Kiểm toán Thực thi Vật lý CSDL (In-Memory DB Sandbox Audit)")
        st.caption("Khởi tạo và chạy thực tế toàn bộ câu lệnh DDL trên SQLite RAM Sandbox (:memory:) để kiểm tra tính khả thi vật lý, cấu trúc khóa chính, toàn vẹn khóa ngoại và tối ưu hóa chỉ mục B-Tree.")

        db_audit = execute_and_audit_ddl(doc.sql_ddl_script)

        health_score = db_audit.get("performance_health_score", 100)
        db_bento_cards = [
            {
                "title": "Khởi tạo RAM Sandbox",
                "value": "PASS (100%)" if db_audit["execution_success"] else "FAIL (0%)",
                "subtitle": "SQLite :memory: Execution",
                "score_pct": 100.0 if db_audit["execution_success"] else 0.0,
                "badge_text": "Khả thi vật lý" if db_audit["execution_success"] else "Lỗi DDL",
                "badge_type": "success" if db_audit["execution_success"] else "danger",
                "icon": "⚙️",
            },
            {
                "title": "Bảng & Chỉ mục B-Tree",
                "value": f"{db_audit['table_count']} Bảng / {db_audit.get('total_indexes_created', 0)} Index",
                "subtitle": "Cấu trúc CSDL vật lý",
                "score_pct": min(100.0, db_audit['table_count'] * 20.0),
                "badge_text": "3NF Physical",
                "badge_type": "info",
                "icon": "🗄️",
            },
            {
                "title": "Ràng buộc Khóa ngoại (FK)",
                "value": f"{db_audit['total_foreign_keys']} Ràng buộc",
                "subtitle": "Toàn vẹn tham chiếu",
                "score_pct": min(100.0, db_audit['total_foreign_keys'] * 25.0),
                "badge_text": "FK Integrity",
                "badge_type": "info",
                "icon": "🔑",
            },
            {
                "title": "Điểm Hiệu năng B-Tree",
                "value": f"{health_score}/100",
                "subtitle": "Leftmost Prefix Coverage",
                "score_pct": float(health_score),
                "badge_text": "Tối ưu hóa B-Tree" if health_score == 100 else ("Cần tối ưu" if health_score >= 80 else "Nguy cơ Scan"),
                "badge_type": "success" if health_score >= 90 else ("warning" if health_score >= 80 else "danger"),
                "icon": "⚡",
            },
        ]
        render_bento_grid(db_bento_cards)

        if not db_audit["execution_success"]:
            st.error(f"❌ Chi tiết sự cố thực thi Sandbox: {db_audit.get('error_message')}")
        else:
            # 1. Cảnh báo Bảng thiếu Primary Key nếu có
            tables_no_pk = db_audit.get("tables_without_pk", [])
            if tables_no_pk:
                st.error(f"🚨 **Phát hiện {len(tables_no_pk)} bảng thiếu Khóa chính (Primary Key):** {', '.join(tables_no_pk)}. Việc thiếu PK vi phạm tính toàn vẹn thực thể 1NF/3NF!")

            # 2. Xử lý Khóa ngoại chưa đánh chỉ mục (Unindexed Foreign Keys)
            unindexed_fks = db_audit.get("unindexed_foreign_keys", [])
            recommended_script = db_audit.get("recommended_index_script", "")

            if unindexed_fks:
                st.warning(
                    f"⚠️ **Cảnh báo Hiệu năng B-Tree Index:** Phát hiện **{len(unindexed_fks)} khóa ngoại (FK)** chưa được đánh chỉ mục theo nguyên lý *Leftmost Prefix*. "
                    "Điều này sẽ dẫn đến quét toàn bảng (**Full Table Scan**) khi thực hiện `JOIN` hoặc `ON DELETE CASCADE` trên bảng lớn trong môi trường Production."
                )

                # Hiển thị bảng chi tiết các FK thiếu index
                unindexed_table = [
                    {
                        "Bảng Chứa FK": item["table"],
                        "Cột Khóa Ngoại": item["fk_column"],
                        "Bảng Tham Chiếu (Parent)": item["referenced_table"],
                        "Câu lệnh Đề xuất Vá Index": item["suggested_ddl"],
                    }
                    for item in unindexed_fks
                ]
                st.dataframe(unindexed_table, use_container_width=True, hide_index=True)

                with st.expander("📄 Xem mã nguồn đề xuất bù đắp B-Tree Index (Recommended Index Script)", expanded=True):
                    st.code(recommended_script, language="sql")

                # Nút tự động chèn index
                if st.button("⚡ Tự động Chèn B-Tree Index Tối ưu vào Kịch bản SQL (Auto-Inject Missing Indexes)", type="primary", key="btn_auto_inject_indexes"):
                    doc.sql_ddl_script = (
                        doc.sql_ddl_script.rstrip()
                        + "\n\n-- =========================================================\n"
                        + "-- AUTO-INJECTED B-TREE INDEXES FOR FOREIGN KEY OPTIMIZATION\n"
                        + "-- =========================================================\n"
                        + recommended_script
                        + "\n"
                    )
                    st.session_state["srs_result"] = doc
                    if "live_workbench_sql" in st.session_state:
                        st.session_state["live_workbench_sql"] = doc.sql_ddl_script
                    st.toast("🚀 Đã tự động chèn chỉ mục B-Tree vào kịch bản SQL và tối ưu hóa 100%!", icon="✅")
                    st.rerun()

            elif not tables_no_pk:
                st.success("🎉 **Hoàn hảo:** Tất cả Khóa chính và Khóa ngoại đều đã được bảo vệ bởi chỉ mục B-Tree (100% Leftmost Prefix Coverage)!")

            # 3. Hiển thị bảng chi tiết cấu trúc các bảng
            if db_audit["tables_metadata"]:
                st.markdown("##### 📋 Chi tiết Cấu trúc Từng Bảng Vật lý")
                tables_summary = [
                    {
                        "Tên Bảng": meta["table_name"],
                        "Có PK?": "✅ Có PK" if meta.get("has_primary_key", True) else "❌ Thiếu PK",
                        "Số Cột": meta["column_count"],
                        "Số Khóa Ngoại": meta["foreign_key_count"],
                        "Cột Đã Đánh Index (Leftmost)": ", ".join(meta.get("leftmost_indexed_columns", [])) if meta.get("leftmost_indexed_columns") else "(Chưa có)",
                        "Bảng Cha Tham Chiếu": ", ".join(meta["referenced_tables"]) if meta["referenced_tables"] else "(Không có)",
                        "Danh Sách Cột (Chi tiết)": ", ".join([f"{c['name']} ({c['type']}{' PK' if c['primary_key'] else ''})" for c in meta["columns"]]),
                    }
                    for meta in db_audit["tables_metadata"]
                ]
                st.dataframe(tables_summary, use_container_width=True, hide_index=True)

            if db_audit.get("warnings"):
                with st.expander("ℹ️ Cảnh báo chuyển đổi chỉ mục (Index Warnings)", expanded=False):
                    for w in db_audit["warnings"]:
                        st.caption(f"⚠️ {w}")

            # 4. Kiểm định Tính Nhất quán Liên Mô hình (Cross-Artifact Consistency: RTM ↔ ERD ↔ SQL)
            st.divider()
            st.markdown("#### 🔗 Kiểm định Tính Nhất quán Liên Mô hình (Cross-Artifact Consistency: RTM ↔ ERD ↔ SQL)")
            st.caption("Đối chiếu tập hợp thực thể trên cả 3 tầng: Ma trận RTM (Tab 1), Sơ đồ ERD 3NF (Tab 3), và Kịch bản SQL DDL (Tab 3) bằng lý thuyết Đại số Tập hợp.")

            consistency_audit = audit_cross_model_consistency(doc)
            c3_cards = [
                {
                    "title": "Đồng bộ Liên Mô hình",
                    "value": f"{consistency_audit['consistency_score']}%",
                    "subtitle": "Đại số Tập hợp RTM ↔ ERD ↔ DDL",
                    "score_pct": float(consistency_audit['consistency_score']),
                    "badge_text": "100% Đồng nhất" if consistency_audit['consistency_score'] == 100 else f"Lệch {100 - consistency_audit['consistency_score']}%",
                    "badge_type": "success" if consistency_audit['consistency_score'] == 100 else "danger",
                    "icon": "🔄",
                },
                {
                    "title": "Tập Bảng RTM (T_RTM)",
                    "value": f"{len(consistency_audit['rtm_tables'])} Bảng",
                    "subtitle": "Traceability Scope",
                    "score_pct": min(100.0, len(consistency_audit['rtm_tables']) * 20.0),
                    "badge_text": "BABOK v3",
                    "badge_type": "info",
                    "icon": "📋",
                },
                {
                    "title": "Thực thể ERD (T_ERD)",
                    "value": f"{len(consistency_audit['erd_entities'])} Thực thể",
                    "subtitle": "Mermaid 3NF Diagram",
                    "score_pct": min(100.0, len(consistency_audit['erd_entities']) * 20.0),
                    "badge_text": "Logical Model",
                    "badge_type": "info",
                    "icon": "🗄️",
                },
                {
                    "title": "Bảng Vật lý (T_DDL)",
                    "value": f"{len(consistency_audit['ddl_tables'])} Bảng",
                    "subtitle": "SQLite RAM Schema",
                    "score_pct": min(100.0, len(consistency_audit['ddl_tables']) * 20.0),
                    "badge_text": "Physical DDL",
                    "badge_type": "info",
                    "icon": "💾",
                },
            ]
            render_bento_grid(c3_cards)

            if not consistency_audit["is_fully_synced"]:
                phantom = consistency_audit.get("phantom_tables_in_rtm", [])
                orphan = consistency_audit.get("orphan_tables_in_ddl", [])
                missing_erd = consistency_audit.get("missing_in_erd", [])

                warning_msgs = []
                if phantom:
                    warning_msgs.append(f"**Bảng có trong RTM nhưng thiếu trong SQL DDL (Phantom Tables):** `{', '.join(phantom)}`")
                if orphan:
                    warning_msgs.append(f"**Bảng có trong SQL DDL nhưng chưa gán trong RTM (Orphan Tables):** `{', '.join(orphan)}`")
                if missing_erd:
                    warning_msgs.append(f"**Bảng trong SQL DDL chưa được vẽ trong ERD (Missing in ERD):** `{', '.join(missing_erd)}`")

                st.warning(
                    "⚠️ **Phát hiện sự không nhất quán giữa các tầng đặc tả:**\n\n" +
                    "\n\n".join(f"- {msg}" for msg in warning_msgs)
                )

                if st.button("🔄 Tự động Đồng bộ Hóa Tên Bảng Liên Mô hình (Auto-Sync Artifacts)", key="btn_sync_artifacts_tab3", type="primary"):
                    synced_doc = auto_sync_rtm_and_erd_with_ddl(doc)
                    st.session_state["srs_result"] = synced_doc
                    st.session_state["live_workbench_erd"] = synced_doc.er_diagram_mermaid
                    st.toast("✅ Đã tự động đồng bộ hóa bảng giữa RTM, ERD và SQL DDL!", icon="🔄")
                    st.rerun()
            else:
                st.success("✅ **100% Nhất quán Liên Mô hình:** Tất cả các bảng trong Ma trận RTM, Sơ đồ ERD và Kịch bản SQL DDL hoàn toàn đồng nhất!")

    # ---------------- TAB 4: ENTERPRISE EXPORT BUNDLE ----------------
    with tab4:
        st.markdown("#### 📦 Xuất Bản & Đóng Gói Hồ Sơ Dự Án (Enterprise Export Bundle)")
        st.caption("Tải về toàn bộ hồ sơ thiết kế đặc tả, kịch bản CSDL, ma trận truy vết RTM và sơ đồ kiến trúc hệ thống đa định dạng.")

        md_content = generate_markdown_report(doc)
        rtm_csv_bytes = generate_rtm_csv_bytes(doc)
        bundle_zip_bytes = create_project_bundle_zip(doc, md_content)

        slug_title = re.sub(r"[^a-zA-Z0-9_\-]+", "_", doc.project_title.lower()).strip("_") or "project"
        zip_filename = f"SRS_Bundle_{slug_title}.zip"
        md_filename = f"01_SRS_{slug_title}.md"
        sql_filename = f"02_Schema_{slug_title}.sql"
        csv_filename = f"03_RTM_{slug_title}.csv"

        col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
        with col_dl1:
            st.download_button(
                label="📦 Tải Trọn bộ Hồ sơ (.ZIP)",
                data=bundle_zip_bytes,
                file_name=zip_filename,
                mime="application/zip",
                type="primary",
                use_container_width=True,
                help="Gói ZIP gồm 7 file: SRS Markdown, SQL DDL, RTM CSV, Model JSON và 3 sơ đồ Mermaid .mmd",
            )
        with col_dl2:
            st.download_button(
                label="📄 Tải Đặc tả SRS (.MD)",
                data=md_content.encode("utf-8"),
                file_name=md_filename,
                mime="text/markdown",
                use_container_width=True,
                help="Tài liệu đặc tả yêu cầu SRS chuẩn IEEE 29148",
            )
        with col_dl3:
            st.download_button(
                label="💾 Tải Kịch bản CSDL (.SQL)",
                data=doc.sql_ddl_script.encode("utf-8"),
                file_name=sql_filename,
                mime="application/sql",
                use_container_width=True,
                help="Kịch bản tạo bảng và khóa ngoại chuẩn 3NF",
            )
        with col_dl4:
            st.download_button(
                label="📊 Tải Ma trận RTM (.CSV - Excel)",
                data=rtm_csv_bytes,
                file_name=csv_filename,
                mime="text/csv",
                use_container_width=True,
                help="Ma trận truy vết yêu cầu chuẩn BABOK v3 (UTF-8 BOM)",
            )

        st.divider()

        tab_prev_md, tab_prev_json = st.tabs([
            "👁️ Xem trước Đặc tả Markdown (IEEE 29148)",
            "🧩 Xem trước Cấu trúc JSON Schema (AST Data)",
        ])
        with tab_prev_md:
            st.text_area("Markdown Preview", value=md_content, height=450)
        with tab_prev_json:
            try:
                st.json(doc.model_dump())
            except Exception:
                st.code(doc.model_dump_json(indent=2), language="json")
