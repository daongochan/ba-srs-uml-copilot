"""Tab 3: Thiết kế CSDL (ERD 3NF & SQL DDL).

Cung cấp DBA Live Workbench để tinh chỉnh ERD/SQL trực tiếp, hiển thị sơ đồ 3NF,
kiểm định cú pháp SQL AST qua sqlglot, chạy kiểm toán SQLite Sandbox in-memory,
phát hiện khóa ngoại chưa đánh chỉ mục B-Tree và tự động vá index.
"""

import streamlit as st
from src.models.srs_schema import SRSDocument
from src.validators.syntax_validator import clean_and_validate_mermaid, validate_sql_ddl
from src.validators.db_sandbox import execute_and_audit_ddl
from src.validators.consistency_checker import (
    audit_cross_model_consistency,
    auto_sync_rtm_and_erd_with_ddl,
)
from src.ui.theme import render_bento_grid
from src.ui.components.mermaid_viewer import render_mermaid


def render_tab_database_design(doc: SRSDocument) -> None:
    """Render nội dung Tab 3: Thiết kế CSDL 3NF, SQL DDL và Sandbox Audit."""
    with st.expander("🛠️ Chế độ Tinh chỉnh Kiến trúc CSDL (DBA Live Workbench)", expanded=False):
        st.caption(
            "Cho phép Kỹ sư CSDL / Solution Architect chỉnh sửa trực tiếp sơ đồ ERD hoặc thêm/sửa bảng, cột, khóa ngoại trong kịch bản SQL DDL để kiểm định lại tức thì."
        )
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
    st.caption(
        "Khởi tạo và chạy thực tế toàn bộ câu lệnh DDL trên SQLite RAM Sandbox (:memory:) để kiểm tra tính khả thi vật lý, cấu trúc khóa chính, toàn vẹn khóa ngoại và tối ưu hóa chỉ mục B-Tree."
    )

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
            "score_pct": min(100.0, db_audit["table_count"] * 20.0),
            "badge_text": "3NF Physical",
            "badge_type": "info",
            "icon": "🗄️",
        },
        {
            "title": "Ràng buộc Khóa ngoại (FK)",
            "value": f"{db_audit['total_foreign_keys']} Ràng buộc",
            "subtitle": "Toàn vẹn tham chiếu",
            "score_pct": min(100.0, db_audit["total_foreign_keys"] * 25.0),
            "badge_text": "FK Integrity",
            "badge_type": "info",
            "icon": "🔑",
        },
        {
            "title": "Điểm Hiệu năng B-Tree",
            "value": f"{health_score}/100",
            "subtitle": "Leftmost Prefix Coverage",
            "score_pct": float(health_score),
            "badge_text": (
                "Tối ưu hóa B-Tree" if health_score == 100 else ("Cần tối ưu" if health_score >= 80 else "Nguy cơ Scan")
            ),
            "badge_type": ("success" if health_score >= 90 else ("warning" if health_score >= 80 else "danger")),
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
            st.error(
                f"🚨 **Phát hiện {len(tables_no_pk)} bảng thiếu Khóa chính (Primary Key):** {', '.join(tables_no_pk)}. Việc thiếu PK vi phạm tính toàn vẹn thực thể 1NF/3NF!"
            )

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

            with st.expander(
                "📄 Xem mã nguồn đề xuất bù đắp B-Tree Index (Recommended Index Script)",
                expanded=True,
            ):
                st.code(recommended_script, language="sql")

            # Nút tự động chèn index
            if st.button(
                "⚡ Tự động Chèn B-Tree Index Tối ưu vào Kịch bản SQL (Auto-Inject Missing Indexes)",
                type="primary",
                key="btn_auto_inject_indexes",
            ):
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
                st.toast(
                    "🚀 Đã tự động chèn chỉ mục B-Tree vào kịch bản SQL và tối ưu hóa 100%!",
                    icon="✅",
                )
                st.rerun()

        elif not tables_no_pk:
            st.success(
                "🎉 **Hoàn hảo:** Tất cả Khóa chính và Khóa ngoại đều đã được bảo vệ bởi chỉ mục B-Tree (100% Leftmost Prefix Coverage)!"
            )

        # 3. Hiển thị bảng chi tiết cấu trúc các bảng
        if db_audit["tables_metadata"]:
            st.markdown("##### 📋 Chi tiết Cấu trúc Từng Bảng Vật lý")
            tables_summary = [
                {
                    "Tên Bảng": meta["table_name"],
                    "Có PK?": "✅ Có PK" if meta.get("has_primary_key", True) else "❌ Thiếu PK",
                    "Số Cột": meta["column_count"],
                    "Số Khóa Ngoại": meta["foreign_key_count"],
                    "Cột Đã Đánh Index (Leftmost)": (
                        ", ".join(meta.get("leftmost_indexed_columns", []))
                        if meta.get("leftmost_indexed_columns")
                        else "(Chưa có)"
                    ),
                    "Bảng Cha Tham Chiếu": (
                        ", ".join(meta["referenced_tables"]) if meta["referenced_tables"] else "(Không có)"
                    ),
                    "Danh Sách Cột (Chi tiết)": ", ".join(
                        [f"{c['name']} ({c['type']}{' PK' if c['primary_key'] else ''})" for c in meta["columns"]]
                    ),
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
        st.caption(
            "Đối chiếu tập hợp thực thể trên cả 3 tầng: Ma trận RTM (Tab 1), Sơ đồ ERD 3NF (Tab 3), và Kịch bản SQL DDL (Tab 3) bằng lý thuyết Đại số Tập hợp."
        )

        consistency_audit = audit_cross_model_consistency(doc)
        c3_cards = [
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
                "badge_type": ("success" if consistency_audit["consistency_score"] == 100 else "danger"),
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
        render_bento_grid(c3_cards)

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
                key="btn_sync_artifacts_tab3",
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
