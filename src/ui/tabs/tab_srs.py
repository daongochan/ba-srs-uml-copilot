"""Tab 1: Đặc tả Yêu cầu (SRS & User Stories).

Hiển thị các chỉ số Bento KPI Grid chuẩn IEEE 29148, cảnh báo linter,
User Stories MoSCoW, Yêu cầu phi chức năng, Ma trận truy vết RTM và
kiểm định tính nhất quán liên mô hình.
"""

import streamlit as st
from src.models.srs_schema import SRSDocument
from src.validators.requirements_linter import evaluate_srs_deterministically
from src.validators.consistency_checker import (
    audit_cross_model_consistency,
    auto_sync_rtm_and_erd_with_ddl,
)
from src.ui.theme import render_bento_grid, render_user_story_card


def render_tab_srs_requirements(doc: SRSDocument) -> None:
    """Render nội dung Tab 1: Đặc tả Yêu cầu SRS, User Stories và RTM."""
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
            "badge_text": (
                "100% Hoàn chỉnh" if rtm_coverage_pct == 100.0 else f"Thiếu {100.0 - rtm_coverage_pct:.1f}%"
            ),
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
        with st.expander(
            "🔍 Báo cáo Kiểm toán Tự động Cú pháp Yêu cầu (Automated Static Linter Report)",
            expanded=True,
        ):
            st.warning(
                f"⚠️ Phát hiện {len(lint_warnings)} cảnh báo chất lượng cần chuẩn hóa cú pháp theo chuẩn IEEE 29148 & INVEST:"
            )
            for w_idx, warning_text in enumerate(lint_warnings, start=1):
                st.markdown(f"**{w_idx}.** {warning_text}")
    else:
        st.success("100% Yêu cầu vượt qua bài kiểm tra từ ngữ mơ hồ và định lượng SLA chuẩn IEEE 29148.")

    # Cảnh báo Điểm Mơ hồ & Câu hỏi Phỏng vấn lại Khách hàng
    if quality_audit and getattr(quality_audit, "clarification_questions", []):
        st.markdown("#### ❓ Cảnh báo Điểm Mơ hồ & Câu hỏi Phỏng vấn lại Khách hàng (Elicitation Follow-up Questions)")
        with st.container(border=True):
            st.warning(
                "⚠️ **Phân tích Rủi ro & Điểm Mơ hồ Nghiệp vụ:** Dựa trên biên bản họp thô, "
                "AI Business Analyst phát hiện các khoảng trống thông tin cần phỏng vấn xác nhận lại với Stakeholders để tránh rủi ro phát sinh phạm vi (Scope Creep):"
            )
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
    st.caption(
        "Mỗi yêu cầu được gắn nhãn ưu tiên MoSCoW và đóng khung kịch bản nghiệm thu Given-When-Then chuẩn Gherkin BDD:"
    )
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
        st.caption(
            "Chuỗi giá trị truy vết theo chuẩn BABOK v3: Mã YC ➔ Tính năng ➔ Quy tắc Nghiệp vụ ➔ Bảng CSDL Liên quan ➔ Kịch bản Kiểm thử Nghiệm thu."
        )
        rtm_table = [
            {
                "Mã YC": item.req_id,
                "Tên Tính năng": item.feature_name,
                "Quy tắc Nghiệp vụ (Business Rule)": item.business_rule,
                "Bảng CSDL Liên quan": (
                    ", ".join(item.related_tables)
                    if isinstance(item.related_tables, list)
                    else str(item.related_tables)
                ),
                "Kịch bản Kiểm thử Nghiệm thu": item.test_scenario_summary,
            }
            for item in traceability_matrix
        ]
        st.dataframe(rtm_table, use_container_width=True, hide_index=True)

    # Kiểm định Tính Nhất quán Liên Mô hình (Cross-Artifact Consistency: RTM ↔ ERD ↔ SQL)
    st.divider()
    st.markdown("#### 🔗 Kiểm định Tính Nhất quán Liên Mô hình (Cross-Artifact Consistency: RTM ↔ ERD ↔ SQL)")
    st.caption(
        "Đối chiếu tập hợp thực thể trên cả 3 tầng: Ma trận RTM (Tab 1), Sơ đồ ERD 3NF (Tab 3), và Kịch bản SQL DDL (Tab 3) bằng lý thuyết Đại số Tập hợp."
    )

    consistency_audit = audit_cross_model_consistency(doc)
    consistency_cards = [
        {
            "title": "Đồng bộ Liên Mô hình",
            "value": f"{consistency_audit['consistency_score']}%",
            "subtitle": "Đại số Tập hợp RTM ↔ ERD ↔ DDL",
            "score_pct": float(consistency_audit["consistency_score"]),
            "badge_text": (
                "100% Đồng nhất"
                if consistency_audit["consistency_score"] == 100
                else f"Lệch {100 - consistency_audit['consistency_score']}%"
            ),
            "badge_type": "success" if consistency_audit["consistency_score"] == 100 else "danger",
            "icon": "🔄",
        },
        {
            "title": "Tập Bảng RTM (T_RTM)",
            "value": f"{len(consistency_audit['rtm_tables'])} Bảng",
            "subtitle": "Traceability Scope",
            "score_pct": min(100.0, len(consistency_audit["rtm_tables"]) * 20.0),
            "badge_text": "BABOK v3",
            "badge_type": "info",
            "icon": "📋",
        },
        {
            "title": "Thực thể ERD (T_ERD)",
            "value": f"{len(consistency_audit['erd_entities'])} Thực thể",
            "subtitle": "Mermaid 3NF Diagram",
            "score_pct": min(100.0, len(consistency_audit["erd_entities"]) * 20.0),
            "badge_text": "Logical Model",
            "badge_type": "info",
            "icon": "🗄️",
        },
        {
            "title": "Bảng Vật lý (T_DDL)",
            "value": f"{len(consistency_audit['ddl_tables'])} Bảng",
            "subtitle": "SQLite RAM Schema",
            "score_pct": min(100.0, len(consistency_audit["ddl_tables"]) * 20.0),
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
            warning_msgs.append(
                f"**Bảng có trong RTM nhưng thiếu trong SQL DDL (Phantom Tables):** `{', '.join(phantom)}`"
            )
        if orphan:
            warning_msgs.append(
                f"**Bảng có trong SQL DDL nhưng chưa gán trong RTM (Orphan Tables):** `{', '.join(orphan)}`"
            )
        if missing_erd:
            warning_msgs.append(
                f"**Bảng trong SQL DDL chưa được vẽ trong ERD (Missing in ERD):** `{', '.join(missing_erd)}`"
            )

        st.warning(
            "⚠️ **Phát hiện sự không nhất quán giữa các tầng đặc tả:**\n\n"
            + "\n\n".join(f"- {msg}" for msg in warning_msgs)
        )

        if st.button(
            "🔄 Tự động Đồng bộ Hóa Tên Bảng Liên Mô hình (Auto-Sync Artifacts)",
            key="btn_sync_artifacts_tab1",
            type="primary",
        ):
            synced_doc = auto_sync_rtm_and_erd_with_ddl(doc)
            st.session_state["srs_result"] = synced_doc
            st.session_state["live_workbench_erd"] = synced_doc.er_diagram_mermaid
            st.toast("✅ Đã tự động đồng bộ hóa bảng giữa RTM, ERD và SQL DDL!", icon="🔄")
            st.rerun()
    else:
        st.success(
            "✅ **100% Nhất quán Liên Mô hình:** Tất cả các bảng trong Ma trận RTM, Sơ đồ ERD và Kịch bản SQL DDL hoàn toàn đồng nhất!"
        )
