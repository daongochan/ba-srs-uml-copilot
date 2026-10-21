"""Streamlit Web Application: AI Business Analyst & System Architect Copilot."""

import os
from typing import Optional
import streamlit as st
from dotenv import load_dotenv

# Nạp biến môi trường từ file .env nếu có
load_dotenv()

from src.models.srs_schema import SRSDocument
from src.services.ai_generator import (
    generate_srs_from_notes,
    generate_srs_with_telemetry,
)
from src.services.telemetry_cache import default_srs_cache, TelemetryMetrics
from src.services.exporter import generate_markdown_report
from src.data.sample_inputs import SAMPLE_SCENARIOS
from src.ui.theme import (
    apply_custom_theme,
    render_clean_html,
    render_header_banner,
    render_telemetry_widget,
)
from src.ui.styles import apply_editorial_styles
from src.ui.components import (
    render_editorial_header,
    render_editorial_kpi_strip,
    render_editorial_empty_state,
    render_editorial_tech_expander,
)
from src.ui.components.mermaid_viewer import render_mermaid
from src.ui.tabs import (
    render_tab_srs_requirements,
    render_tab_dynamic_models,
    render_tab_database_design,
    render_tab_export_bundle,
)
from src.utils.security import sanitize_error_message, MAX_MEETING_NOTES_LENGTH


# Tương thích ngược với các module và test
export_srs_markdown = generate_markdown_report

# Thiết lập cấu hình trang Streamlit
st.set_page_config(
    page_title="AI BA & System Architect Copilot",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Áp dụng bộ quy tắc thiết kế chuẩn Editorial Craft (Tài Liệu Biên Tập)
apply_custom_theme()
apply_editorial_styles()

# Tự động dọn dẹp session_state nếu đối tượng SRSDocument từ phiên cũ thiếu thuộc tính mới
for ss_key in ["srs_result", "doc"]:
    if ss_key in st.session_state and st.session_state[ss_key] is not None:
        if not hasattr(st.session_state[ss_key], "state_diagram_mermaid"):
            st.session_state.pop(ss_key, None)

# -------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    sidebar_header_html = """
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px; padding: 4px 0;">
        <div style="width: 42px; height: 42px; background: linear-gradient(135deg, #0d9488, #0f766e); border-radius: 8px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(13, 148, 136, 0.25); font-size: 20px;">
            📖
        </div>
        <div>
            <div style="font-size: 16px; font-weight: 700; color: #1c1917; line-height: 1.2;">Trung tâm Điều khiển</div>
            <div style="font-size: 11.5px; color: #57534e; font-weight: 500;">Hệ thống Đặc tả & Kiến trúc</div>
        </div>
    </div>
    """
    render_clean_html(sidebar_header_html)

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

    standards_footer = """
    <div style="font-size: 11px; color: #64748b; margin-top: 16px; line-height: 1.6; border-top: 1px solid #e2e8f0; padding-top: 12px;">
        <strong>Hệ quy chiếu Tiêu chuẩn:</strong><br>
        • <b>IEEE 29148:</b> Requirements Engineering<br>
        • <b>BABOK v3:</b> Requirements Traceability Matrix<br>
        • <b>Gherkin BDD:</b> Given - When - Then<br>
        • <b>3NF Sandbox:</b> Boyce-Codd Normal Form<br>
        • <b>Core LLM:</b> <code>gemini-3.8-flash</code>
    </div>
    """
    render_clean_html(standards_footer)

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

# Hỗ trợ chế độ demo trực quan cho visual audit / testing qua query param ?demo=1
if st.query_params.get("demo") == "1" and st.session_state.get("srs_result") is None:
    from tests.test_ui_modular_tabs import _build_test_doc

    st.session_state["srs_result"] = _build_test_doc()

doc_preview: Optional[SRSDocument] = st.session_state.get("srs_result")

# Thanh Tiêu đề Top Navigation Banner với Workflow Stepper
render_editorial_header(has_result=bool(doc_preview))

# Hàng 3 thẻ Kịch bản Nghiệp vụ Mẫu 1-Click
st.markdown("##### 📌 Chọn nhanh Kịch bản Khảo sát mẫu:")
chip_col1, chip_col2, chip_col3 = st.columns(3)
with chip_col1:
    if st.button("🎬 1. Rạp Chiếu Phim (CineMax)", use_container_width=True, help="Khóa ghế 10 phút, đặt vé, chống tranh chấp chỗ ngồi"):
        st.session_state["raw_notes_input"] = SAMPLE_SCENARIOS["cinema_booking"]["meeting_notes"]
        st.rerun()
with chip_col2:
    if st.button("🚌 2. Xe Khách Liên Tỉnh", use_container_width=True, help="Lịch xuất bến, đặt vé xe, trung chuyển hành khách"):
        st.session_state["raw_notes_input"] = SAMPLE_SCENARIOS["bus_logistics"]["meeting_notes"]
        st.rerun()
with chip_col3:
    if st.button("📦 3. Kho Thông Minh (WMS)", use_container_width=True, help="Quản lý tồn kho FIFO, nhập xuất hàng hóa, kiểm kê"):
        st.session_state["raw_notes_input"] = SAMPLE_SCENARIOS["warehouse_inventory"]["meeting_notes"]
        st.rerun()

# Khung nhập Biên bản họp thông minh (Smart Expander: tự mở khi chưa có kết quả, tự thu gọn khi đã có SRS)
with st.expander(
    "📝 Biên bản Ghi chú Cuộc họp Yêu cầu (Meeting Notes)",
    expanded=(doc_preview is None),
):
    st.caption("Dán biên bản khảo sát yêu cầu nghiệp vụ, câu hỏi phỏng vấn stakeholder hoặc quy trình vận hành thô:")
    meeting_notes_text = st.text_area(
        "Nội dung Biên bản Ghi chú Họp Khách hàng (Raw Meeting Notes):",
        value=st.session_state["raw_notes_input"],
        height=220,
        max_chars=MAX_MEETING_NOTES_LENGTH,
        placeholder="Dán nội dung thảo luận với khách hàng, yêu cầu nghiệp vụ, quy trình hoạt động...",
        label_visibility="collapsed",
    )

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        generate_clicked = st.button(
            "🚀 Phân tích Yêu cầu & Tạo Đặc tả",
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
    elif len(meeting_notes_text) > MAX_MEETING_NOTES_LENGTH:
        st.error(
            f"Lỗi: Nội dung ghi chú họp vượt quá giới hạn an toàn ({MAX_MEETING_NOTES_LENGTH:,} ký tự). Vui lòng rút gọn."
        )
    else:
        with st.spinner(
            "🤖 AI Principal BA & Enterprise Architect đang phân tích nghiệp vụ, chuẩn hóa 3NF và sinh sơ đồ..."
        ):
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
                safe_err = sanitize_error_message(e, api_key)
                st.error(f"❌ Quá trình phân tích gặp sự cố: {safe_err}")

# -------------------------------------------------------------
# HIỂN THỊ KẾT QUẢ TRÊN 4 TABS
# -------------------------------------------------------------
doc: Optional[SRSDocument] = st.session_state.get("srs_result")
if doc is not None and not hasattr(doc, "state_diagram_mermaid"):
    st.session_state["srs_result"] = None
    doc = None

if doc:
    st.markdown("---")
    st.subheader(f"📑 Dự án: {doc.project_title}")

    # Dải 4 Thẻ KPI Nghiệp vụ Chuẩn Biên Tập (Editorial KPI Strip)
    render_editorial_kpi_strip(doc, st.session_state.get("telemetry_metrics"))

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "1. Yêu cầu (SRS)",
            "2. Mô hình Động",
            "3. Thiết kế CSDL",
            "4. Xuất bản Hồ sơ",
        ]
    )

    with tab1:
        render_tab_srs_requirements(doc)

    with tab2:
        render_tab_dynamic_models(doc)

    with tab3:
        render_tab_database_design(doc)

    with tab4:
        render_tab_export_bundle(doc)

    # Chi tiết Kỹ thuật & Báo cáo Kiểm toán (Tiết lộ dần)
    render_editorial_tech_expander(st.session_state.get("telemetry_metrics"), doc)
else:
    # Trạng thái ban đầu khi chưa phân tích (Editorial Empty State)
    render_editorial_empty_state()

