"""Exporter service: Generates Markdown reports, RTM CSV and in-memory ZIP bundle."""

import csv
import io
import json
import zipfile
from typing import Optional

from src.models.srs_schema import SRSDocument


def generate_markdown_report(doc: SRSDocument) -> str:
    """Tổng hợp toàn bộ nội dung SRSDocument thành văn bản Markdown chuẩn IEEE 29148 & BABOK v3."""
    lines = [
        f"# {doc.project_title}",
        "",
        "> **Tài liệu Đặc tả Yêu cầu Phần mềm (SRS) & Kiến trúc Hệ thống**",
        "> Tuân thủ chuẩn IEEE 29148, BABOK Guide v3, ISO/IEC 25010 & Third Normal Form (3NF).",
        "",
        "---",
        "",
        "## 1. Mục tiêu Kinh doanh & Phạm vi Hệ thống (Business Objective)",
        f"{doc.business_objective}",
        "",
        "## 2. Danh sách Tác nhân Tham gia (Actors)",
    ]
    for actor in getattr(doc, "actors", []):
        lines.append(f"- **{actor}**")
    lines.extend(["", "## 3. Đặc tả Yêu cầu Chức năng (Functional Requirements)", ""])

    for fr in getattr(doc, "functional_requirements", []):
        lines.append(f"### {fr.req_id}: {fr.title}")
        lines.append(f"- **Độ ưu tiên:** `{fr.priority}`")
        lines.append(f"- **User Story:** *{fr.user_story}*")
        lines.append("")
        lines.append("#### Tiêu chí Chấp nhận (Acceptance Criteria - Gherkin BDD):")
        for idx, ac in enumerate(fr.acceptance_criteria, start=1):
            lines.append(f"**Kịch bản {idx}:**")
            lines.append(f"- **Given:** {ac.given}")
            lines.append(f"- **When:** {ac.when}")
            lines.append(f"- **Then:** {ac.then}")
            lines.append("")

    lines.extend(["## 4. Đặc tả Yêu cầu Phi Chức năng (Non-Functional Requirements)", ""])
    lines.append("| Phân loại | Mô tả yêu cầu (IEEE 29148) | Chỉ số đo lường (Metric / SLA) |")
    lines.append("| :--- | :--- | :--- |")
    for nfr in getattr(doc, "non_functional_requirements", []):
        lines.append(f"| **{nfr.category}** | {nfr.description} | `{nfr.metric}` |")
    lines.append("")

    seq_diag = getattr(doc, "sequence_diagram_mermaid", "")
    lines.extend([
        "## 5. Sơ đồ Tuần tự Nghiệp vụ Trọng tâm (UML Sequence Diagram)",
        "",
        "```mermaid",
        seq_diag.strip() if seq_diag else "",
        "```",
        "",
    ])

    state_diagram = getattr(doc, "state_diagram_mermaid", "")
    state_entity = getattr(doc, "state_machine_entity", "")
    if state_diagram:
        entity_title = f" - {state_entity}" if state_entity else ""
        lines.extend([
            f"## 5.1. Sơ đồ Máy Trạng thái Thực thể Cốt lõi (UML State Machine Diagram){entity_title}",
            "",
            "```mermaid",
            state_diagram.strip(),
            "```",
            "",
        ])

    er_diag = getattr(doc, "er_diagram_mermaid", "")
    sql_script = getattr(doc, "sql_ddl_script", "")
    lines.extend([
        "## 6. Sơ đồ Thực thể Quan hệ Chuẩn 3NF (Mermaid ERD)",
        "",
        "```mermaid",
        er_diag.strip() if er_diag else "",
        "```",
        "",
        "## 7. Kịch bản Khởi tạo Cơ sở Dữ liệu (SQL DDL Script - PostgreSQL)",
        "",
        "```sql",
        sql_script.strip() if sql_script else "",
        "```",
        "",
    ])

    traceability_matrix = getattr(doc, "traceability_matrix", [])
    if traceability_matrix:
        lines.extend([
            "## 8. Ma trận Truy vết Yêu cầu (Requirements Traceability Matrix - RTM)",
            "",
            "| Mã YC | Tên Tính năng | Quy tắc Nghiệp vụ (Business Rule) | Bảng CSDL Liên quan | Kịch bản Kiểm thử Nghiệm thu |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])
        for item in traceability_matrix:
            related = (
                ", ".join(item.related_tables)
                if isinstance(item.related_tables, list)
                else str(item.related_tables or "")
            )
            lines.append(f"| **{item.req_id}** | {item.feature_name} | {item.business_rule} | `{related}` | {item.test_scenario_summary} |")
        lines.append("")

    quality_audit = getattr(doc, "quality_audit", None)
    if quality_audit:
        lines.extend([
            "## 9. Đánh giá Chất lượng Đặc tả & Điểm Cần Phỏng vấn Lại (Quality & Ambiguity Audit)",
            "",
            f"- **Điểm Tuân thủ IEEE 29148:** `{getattr(quality_audit, 'ieee_compliance_score', 90)}/100`",
            f"- **Điểm Chuẩn User Story INVEST:** `{getattr(quality_audit, 'invest_score', 90)}/100`",
            "",
        ])
        if getattr(quality_audit, "third_nf_justification", ""):
            lines.extend([
                "### Giải trình Thiết kế CSDL Đạt Chuẩn 3NF (3NF Justification):",
                f"{quality_audit.third_nf_justification}",
                "",
            ])
        if getattr(quality_audit, "clarification_questions", []):
            lines.extend([
                "### Câu hỏi Đào sâu Nghiệp vụ Cần Xác nhận lại với Stakeholders (Follow-up Questions):",
                "",
            ])
            for q_idx, q in enumerate(quality_audit.clarification_questions, start=1):
                lines.append(f"{q_idx}. {q}")
            lines.append("")

    return "\n".join(lines)


def generate_rtm_csv_bytes(doc: SRSDocument) -> bytes:
    """Xuất Ma trận Truy vết Yêu cầu (RTM) ra định dạng CSV mã hóa utf-8-sig (hỗ trợ Microsoft Excel)."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header chuẩn BABOK v3
    writer.writerow([
        "Mã YC",
        "Tên Tính năng",
        "Quy tắc Nghiệp vụ",
        "Bảng CSDL Liên quan",
        "Kịch bản Kiểm thử Nghiệm thu",
    ])

    traceability_matrix = getattr(doc, "traceability_matrix", []) or []
    for item in traceability_matrix:
        related = (
            ", ".join(item.related_tables)
            if isinstance(item.related_tables, list)
            else str(item.related_tables or "")
        )
        writer.writerow([
            item.req_id,
            item.feature_name,
            item.business_rule,
            related,
            item.test_scenario_summary,
        ])

    return output.getvalue().encode("utf-8-sig")


def create_project_bundle_zip(doc: SRSDocument, markdown_content: str) -> bytes:
    """Đóng gói trọn bộ hồ sơ thiết kế vào file ZIP trong RAM gồm 7 tệp tin."""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. Đặc tả SRS Markdown
        zf.writestr("01_SRS_Specification_IEEE29148.md", markdown_content.encode("utf-8"))

        # 2. Database Schema SQL
        sql_ddl = getattr(doc, "sql_ddl_script", "") or ""
        zf.writestr("02_Database_Schema_3NF.sql", sql_ddl.encode("utf-8"))

        # 3. Traceability Matrix CSV (utf-8-sig)
        rtm_bytes = generate_rtm_csv_bytes(doc)
        zf.writestr("03_Traceability_Matrix_RTM.csv", rtm_bytes)

        # 4. System Architecture Model JSON
        try:
            json_model = doc.model_dump_json(indent=2)
        except Exception:
            json_model = json.dumps(doc.model_dump(), ensure_ascii=False, indent=2)
        zf.writestr("04_System_Architecture_Model.json", json_model.encode("utf-8"))

        # 5. Diagrams (Sequence, State Machine, ERD)
        seq_mermaid = getattr(doc, "sequence_diagram_mermaid", "") or ""
        zf.writestr("diagrams/sequence_diagram.mmd", seq_mermaid.encode("utf-8"))

        state_mermaid = getattr(doc, "state_diagram_mermaid", "") or ""
        zf.writestr("diagrams/state_machine.mmd", state_mermaid.encode("utf-8"))

        erd_mermaid = getattr(doc, "er_diagram_mermaid", "") or ""
        zf.writestr("diagrams/erd_3nf.mmd", erd_mermaid.encode("utf-8"))

    return zip_buffer.getvalue()
