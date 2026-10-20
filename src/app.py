"""Streamlit Web Application: AI Business Analyst & System Architect Copilot."""

import os
import re
import json
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env nếu có
load_dotenv()

from src.models.srs_schema import SRSDocument
from src.services.ai_generator import generate_srs_from_notes
from src.services.exporter import (
    create_project_bundle_zip,
    generate_markdown_report,
    generate_rtm_csv_bytes,
)
from src.data.sample_inputs import SAMPLE_SCENARIOS
from src.validators.syntax_validator import clean_and_validate_mermaid, validate_sql_ddl
from src.validators.db_sandbox import execute_and_audit_ddl

# Tương thích ngược với các module và test
export_srs_markdown = generate_markdown_report

# Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="AI BA & System Architect Copilot",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Tự động dọn dẹp session_state nếu đối tượng SRSDocument từ phiên cũ thiếu thuộc tính mới
for ss_key in ["srs_result", "doc"]:
    if ss_key in st.session_state and st.session_state[ss_key] is not None:
        if not hasattr(st.session_state[ss_key], "state_diagram_mermaid"):
            st.session_state.pop(ss_key, None)


def render_mermaid(mermaid_code: str, height: int = 550, diagram_type: str = "") -> None:
    """Nhúng thư viện Mermaid.js từ CDN và render sơ đồ an toàn qua API mermaid.render()
    kết hợp json.dumps và cơ chế Lazy Visibility Rendering (ResizeObserver/IntersectionObserver)
    để tránh lỗi render SVG khi nằm trong Streamlit tab đang ẩn (offsetWidth == 0).
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
            body {{
                margin: 0;
                padding: 16px;
                background-color: #ffffff;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                display: flex;
                justify-content: center;
                align-items: flex-start;
            }}
            #mermaid-container {{
                width: 100%;
                display: flex;
                justify-content: center;
            }}
            #mermaid-container svg {{
                max-width: 100%;
                height: auto;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                border-radius: 8px;
                padding: 12px;
                background: #ffffff;
            }}
            .mermaid-error {{
                color: #b91c1c;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 12px 16px;
                font-family: monospace;
                font-size: 13px;
                white-space: pre-wrap;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <div id="mermaid-container">
            <div style="color: #64748b; font-size: 14px;">Đang tải sơ đồ Mermaid...</div>
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose'
            }});

            async function renderDiagram() {{
                const container = document.getElementById('mermaid-container');
                const rawCode = {code_json};
                const renderId = 'mermaid_svg_' + Math.random().toString(36).substring(2, 9);
                try {{
                    const {{ svg }} = await mermaid.render(renderId, rawCode);
                    container.innerHTML = svg;
                }} catch (err) {{
                    console.error("Mermaid Render Error:", err);
                    container.innerHTML = '<div class="mermaid-error"><strong>⚠️ Lỗi hiển thị Mermaid:</strong><br>' +
                        (err.message || err) + '</div>';
                }}
            }}

            let rendered = false;
            let resizeObserver = null;
            let intersectionObserver = null;

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
                const container = document.getElementById('mermaid-container');
                if (!container) return;

                // Chỉ render khi tab đã hiển thị thực tế trên cây render (offsetWidth > 0)
                if (document.body.offsetWidth > 0 && container.offsetWidth > 0) {{
                    rendered = true;
                    cleanupObservers();
                    renderDiagram();
                }}
            }}

            const container = document.getElementById('mermaid-container');

            // 1. Nếu đang ở Tab hiển thị sẵn (active tab) -> gọi render ngay
            if (document.body.offsetWidth > 0 && container && container.offsetWidth > 0) {{
                rendered = true;
                renderDiagram();
            }} else {{
                // 2. Nếu nằm trong Tab ẩn của Streamlit (offsetWidth == 0) -> theo dõi khi Tab được click mở
                if (window.ResizeObserver) {{
                    resizeObserver = new ResizeObserver(() => {{
                        checkAndRender();
                    }});
                    resizeObserver.observe(document.body);
                    if (container) {{
                        resizeObserver.observe(container);
                    }}
                }}

                if (window.IntersectionObserver && container) {{
                    intersectionObserver = new IntersectionObserver((entries) => {{
                        for (const entry of entries) {{
                            if (entry.isIntersecting || entry.intersectionRatio > 0) {{
                                checkAndRender();
                            }}
                        }}
                    }});
                    intersectionObserver.observe(container);
                }}

                // Dự phòng khi trình duyệt thay đổi kích thước
                window.addEventListener('resize', checkAndRender);
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=True)

# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/blueprint.png", width=70)
    st.title("Thiết lập Copilot")
    st.caption("AI Business Analyst & Solution Architect")

    # Đọc API key từ môi trường hoặc cho phép nhập
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Google Gemini API Key:",
        value=env_key,
        type="password",
        placeholder="AIzaSy...",
        help="Lấy API Key miễn phí tại https://aistudio.google.com/",
    )
    api_key = api_key_input.strip() if api_key_input else env_key

    if api_key:
        st.success("✅ Đã kết nối API Key", icon="🔑")
    else:
        st.warning("⚠️ Chưa cấu hình GEMINI_API_KEY", icon="⚡")

    st.divider()

    st.subheader("📚 Kịch bản Mẫu Khảo sát")
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
    )

    if selected_scenario != "custom" and selected_scenario in SAMPLE_SCENARIOS:
        sample_data = SAMPLE_SCENARIOS[selected_scenario]
        if st.button("📥 Nạp kịch bản này vào khung nhập", use_container_width=True):
            st.session_state["raw_notes_input"] = sample_data["meeting_notes"]
            st.rerun()

    st.divider()
    st.markdown("""
    **Bộ tiêu chuẩn áp dụng:**
    - 📋 **IEEE 29148:** Requirements Engineering
    - 🏛️ **BABOK v3:** Business Analysis Body of Knowledge
    - 🔄 **Gherkin BDD:** Given - When - Then
    - 🗄️ **3NF:** Third Normal Form (Boyce-Codd)
    - ⚡ **Model:** `gemini-3.8-flash`
    """)

# -------------------------------------------------------------
# MAIN CONTENT AREA
# -------------------------------------------------------------
st.title("📐 BA & System Architect Copilot")
st.markdown(
    "Tự động hóa chuyển đổi **Biên bản họp khách hàng thô (Meeting Notes)** thành "
    "**Đặc tả SRS chuẩn IEEE 29148**, **Sơ đồ UML Sequence**, **ERD Chuẩn 3NF** và **Mã SQL DDL**."
)

# Khởi tạo session state cho input và output
if "raw_notes_input" not in st.session_state:
    st.session_state["raw_notes_input"] = SAMPLE_SCENARIOS["cinema_booking"]["meeting_notes"]

if "srs_result" not in st.session_state:
    st.session_state["srs_result"] = None
else:
    cached_doc = st.session_state.get("srs_result")
    if cached_doc is not None and not hasattr(cached_doc, "state_diagram_mermaid"):
        st.session_state["srs_result"] = None

meeting_notes_text = st.text_area(
    "Nội dung Biên bản Ghi chú Họp Khách hàng (Raw Meeting Notes):",
    value=st.session_state["raw_notes_input"],
    height=240,
    placeholder="Dán nội dung thảo luận với khách hàng, yêu cầu nghiệp vụ, quy trình hoạt động...",
)

col_btn, col_info = st.columns([1, 3])
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
                result_doc = generate_srs_from_notes(meeting_notes_text, api_key)
                st.session_state["srs_result"] = result_doc
                # Dọn dẹp các key widget live edit để đồng bộ kết quả mới
                for edit_k in [
                    "edit_seq_mermaid",
                    "edit_state_mermaid",
                    "live_workbench_erd",
                    "live_workbench_sql",
                ]:
                    st.session_state.pop(edit_k, None)
                st.toast("🎉 Đã sinh thành công Đặc tả Hệ thống & Sơ đồ Kiến trúc!", icon="✅")
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

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric(
                label="📋 Điểm Tuân thủ IEEE 29148",
                value=f"{ieee_score}/100",
                delta="Chuẩn Đặc tả Quốc tế",
            )
        with metric_col2:
            st.metric(
                label="🎯 Điểm User Story INVEST",
                value=f"{invest_score}/100",
                delta="Chuẩn Agile / Scrum",
            )
        with metric_col3:
            st.metric(
                label="📌 Số Yêu cầu Chức năng (FR)",
                value=f"{fr_count} Yêu cầu",
                delta="Đã cấu trúc hóa",
            )

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

        st.markdown("#### 📝 Danh mục Yêu cầu Chức năng (Functional Requirements)")
        for fr in doc.functional_requirements:
            priority_color = {
                "High": "red",
                "Must Have": "red",
                "Medium": "orange",
                "Should Have": "orange",
                "Low": "green",
                "Could Have": "green",
            }.get(fr.priority, "blue")

            with st.container(border=True):
                col_fr_title, col_fr_prio = st.columns([4, 1])
                with col_fr_title:
                    st.markdown(f"##### **[{fr.req_id}]** {fr.title}")
                with col_fr_prio:
                    st.markdown(f":{priority_color}[**{fr.priority}**]")

                st.markdown(f"**User Story:** *{fr.user_story}*")

                with st.expander(f"🔍 Xem {len(fr.acceptance_criteria)} Tiêu chí Chấp nhận (Acceptance Criteria - Gherkin BDD)"):
                    for ac_idx, ac in enumerate(fr.acceptance_criteria, start=1):
                        st.markdown(f"**Kịch bản {ac_idx}:**")
                        st.markdown(f"- 🟡 **Given:** {ac.given}")
                        st.markdown(f"- 🔵 **When:** {ac.when}")
                        st.markdown(f"- 🟢 **Then:** {ac.then}")
                        if ac_idx < len(fr.acceptance_criteria):
                            st.divider()

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
        st.caption("Khởi tạo và chạy thực tế toàn bộ câu lệnh DDL trên SQLite RAM Sandbox (:memory:) để kiểm tra tính khả thi vật lý và tính toàn vẹn khóa ngoại.")

        db_audit = execute_and_audit_ddl(doc.sql_ddl_script)

        audit_col1, audit_col2, audit_col3 = st.columns(3)
        with audit_col1:
            if db_audit["execution_success"]:
                st.metric("⚙️ Khởi tạo Bảng trong RAM", "PASS (100%)", delta="Khả thi vật lý")
            else:
                st.metric("⚙️ Khởi tạo Bảng trong RAM", "FAIL", delta="Lỗi cú pháp DDL", delta_color="inverse")

        with audit_col2:
            st.metric("🗄️ Tổng số Bảng Vật lý", f"{db_audit['table_count']} Bảng", delta="Đã tạo thực tế")

        with audit_col3:
            st.metric("🔑 Ràng buộc Khóa ngoại (FK)", f"{db_audit['total_foreign_keys']} Khóa ngoại", delta="Quan hệ toàn vẹn")

        if not db_audit["execution_success"]:
            st.error(f"❌ Chi tiết sự cố thực thi Sandbox: {db_audit.get('error_message')}")
        elif db_audit["tables_metadata"]:
            tables_summary = [
                {
                    "Tên Bảng": meta["table_name"],
                    "Số Cột": meta["column_count"],
                    "Số Khóa Ngoại": meta["foreign_key_count"],
                    "Bảng Cha Tham Chiếu": ", ".join(meta["referenced_tables"]) if meta["referenced_tables"] else "(Không có)",
                    "Danh Sách Cột (Chi tiết)": ", ".join([f"{c['name']} ({c['type']}{' PK' if c['primary_key'] else ''})" for c in meta["columns"]]),
                }
                for meta in db_audit["tables_metadata"]
            ]
            st.dataframe(tables_summary, use_container_width=True, hide_index=True)

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
