"""Tab 4: Xuất Bản & Đóng Gói Hồ Sơ Dự Án (Enterprise Export Bundle).

Tải về hồ sơ thiết kế đặc tả đa định dạng (ZIP, Markdown, SQL DDL, CSV RTM)
và xem trước nội dung Markdown / JSON Schema AST.
"""

import re
import streamlit as st
from src.models.srs_schema import SRSDocument
from src.services.exporter import (
    create_project_bundle_zip,
    generate_markdown_report,
    generate_rtm_csv_bytes,
)


def render_tab_export_bundle(doc: SRSDocument) -> None:
    """Render nội dung Tab 4: Xuất bản và tải về hồ sơ dự án."""
    st.markdown("#### 📦 Xuất Bản & Đóng Gói Hồ Sơ Dự Án (Enterprise Export Bundle)")
    st.caption(
        "Tải về toàn bộ hồ sơ thiết kế đặc tả, kịch bản CSDL, ma trận truy vết RTM và sơ đồ kiến trúc hệ thống đa định dạng."
    )

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

    tab_prev_md, tab_prev_json = st.tabs(
        [
            "👁️ Xem trước Đặc tả Markdown (IEEE 29148)",
            "🧩 Xem trước Cấu trúc JSON Schema (AST Data)",
        ]
    )
    with tab_prev_md:
        st.text_area("Markdown Preview", value=md_content, height=450)
    with tab_prev_json:
        try:
            st.json(doc.model_dump())
        except Exception:
            st.code(doc.model_dump_json(indent=2), language="json")
