"""Tab 2: Mô hình Động UML (Sequence & State Machine).

Render các sơ đồ tương tác Sequence Diagram và State Machine Diagram
bằng Mermaid SVG, tích hợp tính năng live edit và cập nhật tức thì.
"""

import streamlit as st
from src.models.srs_schema import SRSDocument
from src.validators.syntax_validator import clean_and_validate_mermaid
from src.ui.components.mermaid_viewer import render_mermaid


def render_tab_dynamic_models(doc: SRSDocument) -> None:
    """Render nội dung Tab 2: UML Sequence và State Machine Diagrams."""
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
