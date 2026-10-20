"""Deterministic Requirements Linter for IEEE 29148 and INVEST Standards.

Provides rule-based, deterministic static analysis of Software Requirements
Specification (SRS) documents, user stories, acceptance criteria (Gherkin BDD),
non-functional requirements (NFRs), and requirements traceability matrices (RTM).
"""

import re
from typing import Any, Dict, List, Set
from src.models.srs_schema import SRSDocument


# Các từ ngữ mơ hồ (Weasel Words) bị nghiêm cấm theo chuẩn IEEE 29148
WEASEL_WORD_PATTERNS = [
    (re.compile(r"(?i)\bnhanh chóng\b"), "nhanh chóng"),
    (re.compile(r"(?i)\bdễ dàng\b"), "dễ dàng"),
    (re.compile(r"(?i)\bthân thiện\b"), "thân thiện"),
    (re.compile(r"(?i)\btối ưu(?:\s+hóa)?\b"), "tối ưu"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])v\.v\.?(?:$|[\s,;)\]])"), "v.v."),
    (re.compile(r"(?i)\bfast\b"), "fast"),
    (re.compile(r"(?i)\beasy\b"), "easy"),
    (re.compile(r"(?i)\buser-friendly\b"), "user-friendly"),
    (re.compile(r"(?i)(?:^|[\s,;(\[])etc\.?(?:$|[\s,;)\]])"), "etc."),
]

# Regex kiểm tra cấu trúc chuẩn của User Story
# Tiếng Việt: "Là một... tôi muốn... để..." hoặc "Là... tôi muốn... để..."
VN_USER_STORY_PATTERN = re.compile(
    r"^\s*Là\s+(?:một\s+)?(?P<actor>.+?)[,:]?\s+tôi\s+muốn\s+(?P<action>.+?)\s+để\s+(?P<benefit>.+)",
    re.IGNORECASE | re.DOTALL,
)

# Tiếng Anh: "As a... I want... so that..." hoặc "As an... I want... so that..."
EN_USER_STORY_PATTERN = re.compile(
    r"^\s*As\s+(?:an?\s+|the\s+)?(?P<actor>.+?)[,:]?\s+I\s+want\s+(?P<action>.+?)\s+so\s+that\s+(?P<benefit>.+)",
    re.IGNORECASE | re.DOTALL,
)

# Trọng số trừ điểm chuẩn xác (Deterministic Penalty Weights)
PENALTY_WEASEL_WORD_IEEE = 5
PENALTY_WEASEL_WORD_INVEST = 5
PENALTY_UNQUANTIFIED_NFR_IEEE = 10
PENALTY_INVALID_STORY_FORMAT_INVEST = 15
PENALTY_INVALID_STORY_FORMAT_IEEE = 5
PENALTY_NO_AC_INVEST = 15
PENALTY_NO_AC_IEEE = 10
PENALTY_EMPTY_BDD_INVEST = 10
PENALTY_EMPTY_BDD_IEEE = 5
PENALTY_SHORT_THEN_INVEST = 5
PENALTY_SHORT_THEN_IEEE = 5


def _scan_weasel_words(text: str) -> List[str]:
    """Quét tìm tất cả các từ ngữ mơ hồ (Weasel Words) trong một đoạn văn bản."""
    if not text:
        return []
    found: List[str] = []
    for pattern, word in WEASEL_WORD_PATTERNS:
        if pattern.search(text):
            found.append(word)
    return found


def evaluate_srs_deterministically(doc: SRSDocument) -> Dict[str, Any]:
    """Phân tích tĩnh và chấm điểm xác định (deterministic) cho tài liệu SRS dựa trên
    chuẩn quốc tế IEEE 29148 và tiêu chuẩn Agile INVEST.

    Các tiêu chí kiểm tra:
    1. Phát hiện từ ngữ mơ hồ (Weasel Words) trong user_story và acceptance_criteria.
    2. Cấu trúc chuẩn của user_story ("Là một... tôi muốn... để..." hoặc "As a... I want... so that...").
    3. Chất lượng Gherkin BDD (given, when, then không được rỗng; mệnh đề then >= 15 ký tự).
    4. Yêu cầu phi chức năng (NFRs) bắt buộc chứa số liệu định lượng (\\d+).
    5. Tính toàn vẹn của Ma trận Truy vết (traceability_matrix): 100% req_id trong functional_requirements phải xuất hiện.

    Args:
        doc: Đối tượng SRSDocument cần kiểm định.

    Returns:
        dict chứa:
            - deterministic_ieee_score (int): 0-100
            - deterministic_invest_score (int): 0-100
            - rtm_coverage_pct (float): 0.0-100.0
            - lint_warnings (List[str]): Danh sách cảnh báo chi tiết
            - stats (dict): Thống kê chi tiết các vi phạm
    """
    if doc is None:
        raise ValueError("Tài liệu SRSDocument không được để trống (None).")

    lint_warnings: List[str] = []

    # Bộ đếm vi phạm
    weasel_count = 0
    format_issue_count = 0
    no_ac_count = 0
    bdd_empty_count = 0
    bdd_short_then_count = 0
    unquantified_nfr_count = 0

    functional_requirements = getattr(doc, "functional_requirements", []) or []
    non_functional_requirements = getattr(doc, "non_functional_requirements", []) or []
    traceability_matrix = getattr(doc, "traceability_matrix", []) or []

    # 1. Kiểm tra Functional Requirements & User Stories
    if not functional_requirements:
        lint_warnings.append(
            "[SRS] Tài liệu chưa có bất kỳ Yêu cầu Chức năng (Functional Requirement) nào."
        )

    for fr in functional_requirements:
        req_id = getattr(fr, "req_id", "FR-??")
        user_story = (getattr(fr, "user_story", "") or "").strip()

        # 1.1 Quét từ ngữ mơ hồ trong User Story
        weasels_in_story = _scan_weasel_words(user_story)
        for w in weasels_in_story:
            weasel_count += 1
            lint_warnings.append(
                f"[{req_id}] User Story chứa từ ngữ mơ hồ (Weasel Word): '{w}'. "
                "Khuyến nghị thay thế bằng tiêu chí đo lường chính xác."
            )

        # 1.2 Kiểm tra cấu trúc chuẩn của User Story
        if user_story:
            is_valid_format = bool(
                VN_USER_STORY_PATTERN.match(user_story)
                or EN_USER_STORY_PATTERN.match(user_story)
            )
            if not is_valid_format:
                format_issue_count += 1
                lint_warnings.append(
                    f"[{req_id}] User Story không đúng cấu trúc chuẩn "
                    "('Là một... tôi muốn... để...' hoặc 'As a... I want... so that...'): "
                    f"'{user_story}'"
                )
        else:
            format_issue_count += 1
            lint_warnings.append(f"[{req_id}] User Story bị để trống.")

        # 1.3 Kiểm tra Tiêu chí Chấp nhận (Acceptance Criteria - Gherkin BDD)
        acceptance_criteria = getattr(fr, "acceptance_criteria", []) or []
        if not acceptance_criteria:
            no_ac_count += 1
            lint_warnings.append(
                f"[{req_id}] Chưa định nghĩa Tiêu chí Chấp nhận (Acceptance Criteria) nào "
                "(Vi phạm chuẩn INVEST: Thiếu tính Testable)."
            )
        else:
            for ac_idx, ac in enumerate(acceptance_criteria, start=1):
                given = (getattr(ac, "given", "") or "").strip()
                when = (getattr(ac, "when", "") or "").strip()
                then = (getattr(ac, "then", "") or "").strip()

                # Quét từ ngữ mơ hồ trong AC
                for clause_name, clause_val in [
                    ("Given", given),
                    ("When", when),
                    ("Then", then),
                ]:
                    for w in _scan_weasel_words(clause_val):
                        weasel_count += 1
                        lint_warnings.append(
                            f"[{req_id}] Tiêu chí chấp nhận #{ac_idx} ({clause_name}) "
                            f"chứa từ ngữ mơ hồ (Weasel Word): '{w}'."
                        )

                # Kiểm tra rỗng
                if not given:
                    bdd_empty_count += 1
                    lint_warnings.append(
                        f"[{req_id}] Tiêu chí chấp nhận #{ac_idx}: Mệnh đề 'Given' bị để trống."
                    )
                if not when:
                    bdd_empty_count += 1
                    lint_warnings.append(
                        f"[{req_id}] Tiêu chí chấp nhận #{ac_idx}: Mệnh đề 'When' bị để trống."
                    )
                if not then:
                    bdd_empty_count += 1
                    lint_warnings.append(
                        f"[{req_id}] Tiêu chí chấp nhận #{ac_idx}: Mệnh đề 'Then' bị để trống."
                    )
                elif len(then) < 15:
                    # Mệnh đề then phải đủ chi tiết >= 15 ký tự
                    bdd_short_then_count += 1
                    lint_warnings.append(
                        f"[{req_id}] Tiêu chí chấp nhận #{ac_idx}: Mệnh đề 'Then' quá ngắn "
                        f"({len(then)} ký tự < 15 ký tự tối thiểu), chưa đủ chi tiết để kiểm thử nghiệm thu: '{then}'"
                    )

    # 2. Kiểm tra Yêu cầu Phi chức năng (Non-Functional Requirements)
    if not non_functional_requirements:
        lint_warnings.append(
            "[SRS] Tài liệu chưa có bất kỳ Yêu cầu Phi chức năng (NFR) nào."
        )

    for nfr in non_functional_requirements:
        category = getattr(nfr, "category", "NFR")
        metric_str = (getattr(nfr, "metric", "") or "").strip()
        desc_str = (getattr(nfr, "description", "") or "").strip()
        combined_text = f"{metric_str} {desc_str}"

        # Bắt buộc phải chứa số liệu định lượng (\\d+)
        if not re.search(r"\d+", combined_text):
            unquantified_nfr_count += 1
            lint_warnings.append(
                f"[NFR - {category}] Yêu cầu phi chức năng thiếu chỉ số định lượng đo lường được "
                f"(bắt buộc chứa số liệu SLA / ngưỡng định lượng): '{metric_str or desc_str}'"
            )

    # 3. Kiểm tra tính toàn vẹn của Ma trận Truy vết (Requirements Traceability Matrix)
    fr_ids: List[str] = [
        fr.req_id.strip()
        for fr in functional_requirements
        if getattr(fr, "req_id", None) and fr.req_id.strip()
    ]

    rtm_ids: Set[str] = set()
    for item in traceability_matrix:
        raw_rid = getattr(item, "req_id", "") or ""
        for chunk in re.split(r"[,;\s]+", raw_rid.strip()):
            cleaned_rid = chunk.strip().upper()
            if cleaned_rid:
                rtm_ids.add(cleaned_rid)

    covered_ids: List[str] = [rid for rid in fr_ids if rid.upper() in rtm_ids]
    missing_ids: List[str] = [rid for rid in fr_ids if rid.upper() not in rtm_ids]

    if not fr_ids:
        rtm_coverage_pct = 100.0
    else:
        rtm_coverage_pct = round((len(covered_ids) / len(fr_ids)) * 100.0, 1)

    for missing_id in missing_ids:
        lint_warnings.append(
            f"[{missing_id}] Yêu cầu chức năng chưa được ánh xạ trong Ma trận Truy vết "
            "(Thiếu trong Requirements Traceability Matrix - RTM)."
        )

    # 4. Tính toán điểm IEEE 29148 (Deterministic Linter)
    # Tiêu chuẩn IEEE 29148: Tính chính xác, không mơ hồ, đo lường được, truy vết được.
    ieee_deductions = 0
    ieee_deductions += weasel_count * PENALTY_WEASEL_WORD_IEEE
    ieee_deductions += unquantified_nfr_count * PENALTY_UNQUANTIFIED_NFR_IEEE
    ieee_deductions += format_issue_count * PENALTY_INVALID_STORY_FORMAT_IEEE
    ieee_deductions += no_ac_count * PENALTY_NO_AC_IEEE
    ieee_deductions += bdd_empty_count * PENALTY_EMPTY_BDD_IEEE
    ieee_deductions += bdd_short_then_count * PENALTY_SHORT_THEN_IEEE

    # Khấu trừ nếu độ phủ RTM < 100%
    if rtm_coverage_pct < 100.0:
        rtm_penalty = int(round((100.0 - rtm_coverage_pct) * 0.25))
        ieee_deductions += rtm_penalty

    if not functional_requirements:
        ieee_deductions += 40
    if not non_functional_requirements:
        ieee_deductions += 20

    deterministic_ieee_score = max(0, min(100, 100 - ieee_deductions))

    # 5. Tính toán điểm INVEST (Rule-based)
    # Tiêu chuẩn INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable
    invest_deductions = 0
    invest_deductions += format_issue_count * PENALTY_INVALID_STORY_FORMAT_INVEST
    invest_deductions += weasel_count * PENALTY_WEASEL_WORD_INVEST
    invest_deductions += no_ac_count * PENALTY_NO_AC_INVEST
    invest_deductions += bdd_empty_count * PENALTY_EMPTY_BDD_INVEST
    invest_deductions += bdd_short_then_count * PENALTY_SHORT_THEN_INVEST

    if not functional_requirements:
        invest_deductions += 50

    deterministic_invest_score = max(0, min(100, 100 - invest_deductions))

    return {
        "deterministic_ieee_score": deterministic_ieee_score,
        "deterministic_invest_score": deterministic_invest_score,
        "rtm_coverage_pct": rtm_coverage_pct,
        "lint_warnings": lint_warnings,
        "stats": {
            "weasel_count": weasel_count,
            "format_issue_count": format_issue_count,
            "no_ac_count": no_ac_count,
            "bdd_empty_count": bdd_empty_count,
            "bdd_short_then_count": bdd_short_then_count,
            "unquantified_nfr_count": unquantified_nfr_count,
            "total_fr_count": len(fr_ids),
            "covered_rtm_count": len(covered_ids),
            "missing_rtm_ids": missing_ids,
        },
    }
