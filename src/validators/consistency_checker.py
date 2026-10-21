r"""Cross-Model Consistency Verifier between RTM, ERD, and SQL DDL based on Set Theory."""

import re
from typing import Dict, Any, Set, List
import sqlglot
from sqlglot import exp

from src.models.srs_schema import SRSDocument, TraceabilityItem


def extract_ddl_tables(sql_code: str) -> Set[str]:
    """Trích xuất tập hợp tên các bảng vật lý được định nghĩa trong câu lệnh SQL DDL.
    
    Chuẩn hóa tất cả tên bảng về chữ thường (lowercase) và loại bỏ quotes/schema prefixes.
    """
    if not sql_code or not sql_code.strip():
        return set()

    cleaned_sql = sql_code.strip()
    cleaned_sql = re.sub(r"^```(?:sql)?\s*\n?", "", cleaned_sql, flags=re.IGNORECASE).strip()
    cleaned_sql = re.sub(r"\n?```\s*$", "", cleaned_sql).strip()

    tables: Set[str] = set()

    # 1. Thử parse bằng sqlglot AST Parser
    try:
        try:
            expressions = sqlglot.parse(cleaned_sql, read="postgres")
        except Exception:
            expressions = sqlglot.parse(cleaned_sql)

        for expr in expressions:
            if expr is None:
                continue
            if isinstance(expr, exp.Create):
                kind = str(getattr(expr, "kind", "")).upper()
                if kind == "TABLE" or "CREATE TABLE" in expr.sql().upper():
                    table_expr = expr.this
                    if table_expr:
                        if isinstance(table_expr, exp.Schema):
                            tbl_name = table_expr.this.name if hasattr(table_expr.this, "name") else str(table_expr.this)
                        elif hasattr(table_expr, "name"):
                            tbl_name = table_expr.name
                        else:
                            tbl_name = str(table_expr)
                        clean_name = re.sub(r"[\"\'`\[\]]", "", tbl_name).strip().lower()
                        if clean_name and not clean_name.startswith("sqlite_"):
                            tables.add(clean_name)
    except Exception:
        pass

    # 2. Sử dụng Regex làm lớp bảo vệ dự phòng (Fallback Regex)
    regex_pattern = r"(?i)\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[\"\'`]?\w+[\"\'`]?\.)?[\"\'`]?([A-Za-z0-9_]+)[\"\'`]?"
    matches = re.findall(regex_pattern, cleaned_sql)
    for m in matches:
        clean_m = m.strip().lower()
        if clean_m and not clean_m.startswith("sqlite_"):
            tables.add(clean_m)

    return tables


def extract_erd_entities(erd_mermaid: str) -> Set[str]:
    """Trích xuất tập hợp tên các thực thể từ sơ đồ Mermaid ERD.
    
    Chuẩn hóa tên thực thể về chữ thường (lowercase) và loại bỏ hoàn toàn các thuộc tính bên trong { }.
    """
    if not erd_mermaid or not erd_mermaid.strip():
        return set()

    cleaned_erd = erd_mermaid.strip()
    cleaned_erd = re.sub(r"^```(?:mermaid)?\s*\n?", "", cleaned_erd, flags=re.IGNORECASE).strip()
    cleaned_erd = re.sub(r"\n?```\s*$", "", cleaned_erd).strip()

    entities: Set[str] = set()

    # 1. Trích xuất từ các khối thực thể có ngoặc nhọn: ENTITY_NAME { ... }
    block_matches = re.findall(r"^\s*([A-Za-z0-9_]+)\s*\{", cleaned_erd, flags=re.MULTILINE)
    for ent in block_matches:
        clean_ent = ent.strip().lower()
        if clean_ent not in {"erdiagram", "direction"}:
            entities.add(clean_ent)

    # 2. Loại bỏ toàn bộ phần thân thuộc tính { ... } để tránh nhận diện nhầm trường thành tên thực thể
    erd_without_blocks = re.sub(r"\{[^}]*\}", "", cleaned_erd)

    # 3. Trích xuất từ các dòng quan hệ: ENTITY_A ||--o{ ENTITY_B : label
    # Ký hiệu quan hệ trong Mermaid ERD có thể chứa: |, {, }, o, ., -, <, >
    rel_regex = r"^\s*([A-Za-z0-9_]+)\s+([\|\{\}o\.\-\<\>]+)\s+([A-Za-z0-9_]+)(?:\s*:\s*.*)?$"
    for line in erd_without_blocks.splitlines():
        line = line.strip()
        if not line or line.startswith("%%") or line.lower().startswith("erdiagram") or line.lower().startswith("direction"):
            continue

        match = re.match(rel_regex, line)
        if match:
            left_ent = match.group(1).strip().lower()
            rel_symbols = match.group(2).strip()
            right_ent = match.group(3).strip().lower()
            # Xác thực chuỗi nối là ký hiệu quan hệ của Mermaid ERD (có chứa nét nối -- hoặc ..)
            if any(sym in rel_symbols for sym in ("--", "..")):
                if left_ent not in {"erdiagram", "direction"}:
                    entities.add(left_ent)
                if right_ent not in {"erdiagram", "direction"}:
                    entities.add(right_ent)
        elif re.match(r"^[A-Za-z0-9_]+$", line):
            clean_line = line.strip().lower()
            if clean_line not in {"erdiagram", "direction"}:
                entities.add(clean_line)

    return entities


def audit_cross_model_consistency(doc: SRSDocument) -> Dict[str, Any]:
    r"""Kiểm toán tính nhất quán liên mô hình giữa Ma trận RTM, Sơ đồ ERD và Kịch bản SQL DDL
    dựa trên lý thuyết Đại số Tập hợp (Set Operations).
    
    Args:
        doc: Đối tượng SRSDocument chứa RTM, ERD, và SQL DDL.
        
    Returns:
        dict: Chứa:
            - rtm_tables (List[str]): Danh sách bảng trong RTM.
            - erd_entities (List[str]): Danh sách thực thể trong ERD.
            - ddl_tables (List[str]): Danh sách bảng trong SQL DDL.
            - phantom_tables_in_rtm (List[str]): T_RTM \ T_DDL (bảng có trong RTM nhưng thiếu trong DDL).
            - orphan_tables_in_ddl (List[str]): T_DDL \ T_RTM (bảng có trong DDL nhưng chưa gán vào RTM).
            - missing_in_erd (List[str]): T_DDL \ T_ERD (bảng trong DDL chưa được vẽ trong ERD).
            - consistency_score (int): Điểm nhất quán (0-100%).
            - is_fully_synced (bool): True nếu đạt 100% nhất quán giữa cả 3 tầng.
    """
    # 1. Tập hợp bảng trong RTM: T_RTM
    rtm_tables_set: Set[str] = set()
    traceability_matrix = getattr(doc, "traceability_matrix", []) or []
    for item in traceability_matrix:
        rel_tables = getattr(item, "related_tables", [])
        if isinstance(rel_tables, list):
            for t in rel_tables:
                for sub_t in str(t).split(","):
                    clean_t = sub_t.strip().lower()
                    if clean_t:
                        rtm_tables_set.add(clean_t)
        elif isinstance(rel_tables, str):
            for sub_t in rel_tables.split(","):
                clean_t = sub_t.strip().lower()
                if clean_t:
                    rtm_tables_set.add(clean_t)

    # 2. Tập hợp thực thể trong ERD: T_ERD
    erd_code = getattr(doc, "er_diagram_mermaid", "") or ""
    erd_entities_set: Set[str] = extract_erd_entities(erd_code)

    # 3. Tập hợp bảng trong SQL DDL: T_DDL
    sql_code = getattr(doc, "sql_ddl_script", "") or ""
    ddl_tables_set: Set[str] = extract_ddl_tables(sql_code)

    # 4. Đại số Tập hợp (Set Differences)
    phantom_tables_in_rtm = sorted(list(rtm_tables_set - ddl_tables_set))
    orphan_tables_in_ddl = sorted(list(ddl_tables_set - rtm_tables_set))
    missing_in_erd = sorted(list(ddl_tables_set - erd_entities_set))

    is_fully_synced = (
        len(phantom_tables_in_rtm) == 0
        and len(orphan_tables_in_ddl) == 0
        and len(missing_in_erd) == 0
    )

    # 5. Tính điểm nhất quán (0 - 100%)
    all_distinct = rtm_tables_set | erd_entities_set | ddl_tables_set
    if not all_distinct:
        consistency_score = 100
    elif is_fully_synced:
        consistency_score = 100
    else:
        # Giao điểm của cả 3 tập hợp
        intersection = rtm_tables_set & erd_entities_set & ddl_tables_set
        raw_score = int(round((len(intersection) / len(all_distinct)) * 100))
        # Khấu trừ có trọng số nếu intersection = 0 nhưng có độ tương đồng từng phần
        pairwise_rtm_ddl = rtm_tables_set & ddl_tables_set
        pairwise_erd_ddl = erd_entities_set & ddl_tables_set
        if not intersection and (pairwise_rtm_ddl or pairwise_erd_ddl):
            partial_score = int(round(((len(pairwise_rtm_ddl) + len(pairwise_erd_ddl)) / (2 * len(ddl_tables_set or all_distinct))) * 100))
            consistency_score = max(raw_score, min(95, partial_score))
        else:
            consistency_score = raw_score

    return {
        "rtm_tables": sorted(list(rtm_tables_set)),
        "erd_entities": sorted(list(erd_entities_set)),
        "ddl_tables": sorted(list(ddl_tables_set)),
        "phantom_tables_in_rtm": phantom_tables_in_rtm,
        "orphan_tables_in_ddl": orphan_tables_in_ddl,
        "missing_in_erd": missing_in_erd,
        "consistency_score": consistency_score,
        "is_fully_synced": is_fully_synced,
    }


def auto_sync_rtm_and_erd_with_ddl(doc: SRSDocument) -> SRSDocument:
    """Tự động đồng bộ hóa bảng giữa RTM và ERD theo nguồn chân lý (Source of Truth) là SQL DDL.
    
    Quy tắc đồng bộ:
    1. Với RTM: Thay thế các bảng không tồn tại (phantom tables) bằng các bảng DDL chưa được gán (orphan tables).
       Nếu còn bảng DDL chưa được gán, tự động bổ sung vào ma trận RTM để đạt 100% độ phủ.
    2. Với ERD: Nếu có bảng trong SQL DDL chưa xuất hiện trong ERD, tự động nối thêm khối định nghĩa thực thể
       chuẩn Mermaid vào cuối sơ đồ.
    """
    ddl_tables = extract_ddl_tables(doc.sql_ddl_script)
    if not ddl_tables:
        return doc

    audit = audit_cross_model_consistency(doc)
    phantom_rtm = audit["phantom_tables_in_rtm"]
    orphan_ddl = audit["orphan_tables_in_ddl"]
    missing_erd = audit["missing_in_erd"]

    # 1. Đồng bộ hóa RTM
    mapping: Dict[str, str] = {}
    remaining_orphan = list(orphan_ddl)
    for p in phantom_rtm:
        if remaining_orphan:
            mapping[p] = remaining_orphan.pop(0)

    new_traceability: List[TraceabilityItem] = []
    assigned_ddl_tables: Set[str] = set()

    for item in doc.traceability_matrix:
        updated_related: List[str] = []
        for t in item.related_tables:
            clean_t = t.strip().lower()
            if clean_t in mapping:
                target_t = mapping[clean_t]
                updated_related.append(target_t)
                assigned_ddl_tables.add(target_t)
            elif clean_t in ddl_tables:
                updated_related.append(clean_t)
                assigned_ddl_tables.add(clean_t)

        dedup_related = list(dict.fromkeys(updated_related))
        new_item = item.model_copy(update={"related_tables": dedup_related})
        new_traceability.append(new_item)

    uncovered_ddl = sorted(list(ddl_tables - assigned_ddl_tables))
    if uncovered_ddl:
        if new_traceability:
            first_item = new_traceability[0]
            merged_tables = list(dict.fromkeys(first_item.related_tables + uncovered_ddl))
            new_traceability[0] = first_item.model_copy(update={"related_tables": merged_tables})
        else:
            new_traceability.append(
                TraceabilityItem(
                    req_id="FR-SYNC-01",
                    feature_name="Physical Data Architecture",
                    business_rule="Tất cả dữ liệu vật lý phải được lưu trữ nhất quán theo chuẩn 3NF",
                    related_tables=uncovered_ddl,
                    test_scenario_summary="Kiểm tra tính toàn vẹn dữ liệu và ràng buộc khóa trên các bảng vật lý",
                )
            )

    doc.traceability_matrix = new_traceability

    # 2. Đồng bộ hóa ERD
    if missing_erd:
        erd_text = doc.er_diagram_mermaid.rstrip()
        append_lines = ["\n    %% Auto-synced entities from Physical SQL DDL"]
        for tbl in sorted(list(missing_erd)):
            entity_name = tbl.upper()
            append_lines.append(f"    {entity_name} {{")
            append_lines.append("        int id PK \"Surrogate Primary Key\"")
            append_lines.append("    }")
        doc.er_diagram_mermaid = erd_text + "\n" + "\n".join(append_lines) + "\n"

    return doc
