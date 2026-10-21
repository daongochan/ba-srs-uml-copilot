"""AI Generation service using Google GenAI SDK to produce structured SRS documents."""

import json
import time
from typing import Tuple
from google import genai
from google.genai import types

from src.models.srs_schema import SRSDocument
from src.validators.syntax_validator import clean_and_validate_mermaid, validate_sql_ddl
from src.services.telemetry_cache import (
    TelemetryMetrics,
    compute_content_hash,
    default_srs_cache,
    execute_with_exponential_backoff,
)

SYSTEM_INSTRUCTION = """Bạn là một Principal Business Analyst (sở hữu chứng chỉ quốc tế IIBA CBAP) kiêm Senior Enterprise & Database Architect với hơn 15 năm kinh nghiệm.
Nhiệm vụ của bạn là chuyển hóa các ghi chú thô từ buổi họp khách hàng (Meeting Notes) thành một bản Đặc tả Yêu cầu Phần mềm (SRS - Software Requirements Specification) hoàn chỉnh, chuẩn mực, chặt chẽ và sẵn sàng cho đội ngũ phát triển.

CÁC NGUYÊN TẮC BẮT BUỘC:
1. Chuẩn hóa IEEE 29148 & BABOK Guide v3:
   - project_title: Tên hệ thống chuyên nghiệp, súc tích.
   - business_objective: Mục tiêu kinh doanh cốt lõi (Business Objective & Scope), phân tích giá trị giải pháp mang lại cho tổ chức.
   - actors: Danh sách toàn bộ các vai trò, tác nhân (con người hoặc hệ thống bên thứ ba) tương tác với hệ thống.
   - functional_requirements: Danh sách tối thiểu 4-6 yêu cầu chức năng trọng tâm. Mỗi yêu cầu phải có mã chuẩn (FR-01, FR-02,...), tiêu đề rõ ràng, User Story chuẩn định dạng "Là [tác nhân], tôi muốn [hành động], để [mục đích]", độ ưu tiên theo chuẩn MoSCoW (Must Have / Should Have / Could Have) hoặc High/Medium/Low.
   - acceptance_criteria: Bắt buộc viết theo chuẩn Gherkin BDD với bộ 3:
     + given: Tiền điều kiện hoặc trạng thái ban đầu của hệ thống.
     + when: Hành động hoặc sự kiện kích hoạt từ tác nhân.
     + then: Kết quả mong đợi và trạng thái thay đổi của hệ thống.
   - non_functional_requirements: Tối thiểu 3-5 yêu cầu phi chức năng phân loại theo chuẩn ISO/IEC 25010 (Security, Performance, Scalability, Reliability, Usability...), có mô tả chi tiết và chỉ số đo lường (metric) định lượng cụ thể (ví dụ: SLA 99.9%, Response time < 200ms với 5000 CCU, Mã hóa AES-256,...).

2. Thiết kế Sơ đồ Tuần tự (Mermaid Sequence Diagram) - QUY TẮC NGHIÊM NGẶT:
   - sequence_diagram_mermaid: BẮT BUỘC bắt đầu trực tiếp bằng từ khóa 'sequenceDiagram'.
   - Minh họa trực quan và logic luồng nghiệp vụ quan trọng nhất (Happy path và nhánh ngoại lệ/thanh toán).
   - QUY TẮC BẮT BUỘC: Mọi participant/actor phải khai báo ID tiếng Anh viết liền và đặt tên tiếng Việt trong ngoặc kép (Ví dụ: `participant U as "Khach Hang"`, `actor C as "Nguoi Dung"`).
   - Nội dung thông điệp sau dấu hai chấm `:` tuyệt đối KHÔNG được chứa dấu chấm phẩy `;` hay ngoặc nhọn `{}`.
   - Sử dụng cú pháp Mermaid chuẩn: `autonumber`, thông điệp đồng bộ/bất đồng bộ (`->>`, `-->>`), khối `alt / else` hoặc `opt` phân nhánh.
   - Không chứa bất kỳ thẻ markdown thừa nào trong chuỗi (như ```mermaid hoặc ```).

3. Thiết kế Cơ sở dữ liệu Chuẩn 3NF & Sơ đồ ERD (Mermaid ER Diagram) - QUY TẮC NGHIÊM NGẶT:
   - er_diagram_mermaid: BẮT BUỘC bắt đầu trực tiếp bằng từ khóa 'erDiagram'.
   - Mô hình hóa các thực thể đạt Chuẩn dạng 3 (3NF): Loại bỏ trùng lặp dữ liệu (1NF), loại bỏ phụ thuộc một phần (2NF), loại bỏ triệt để phụ thuộc bắc cầu (3NF).
   - Tên bảng chỉ dùng chữ cái tiếng Anh và dấu gạch dưới (snake_case hoặc UPPER_CASE).
   - Bên trong khối `{ }`, mỗi dòng chỉ gồm: `<type> <attribute_name> <PK/FK> "<comment>"`
   - Tuyệt đối KHÔNG viết kích thước trong ngoặc đơn ở kiểu dữ liệu (chỉ viết `varchar`, `int`, `decimal`, `timestamp`... - KHÔNG ĐƯỢC viết `varchar(50)` hay `decimal(10, 2)`).
   - Tuyệt đối KHÔNG có dấu phẩy `,` ở cuối dòng bên trong khối `{ }`.
   - Comment chú thích bắt buộc bọc trong dấu ngoặc kép `""` (Ví dụ: `varchar username PK "Ten dang nhap"`).
   - Khai báo các thực thể với thuộc tính, khóa chính (PK), khóa ngoại (FK) và mối quan hệ chính xác (ví dụ: ||--o{, ||--|{).

4. Kịch bản SQL DDL (PostgreSQL / ANSI SQL Standard):
   - sql_ddl_script: Chứa toàn bộ các câu lệnh `CREATE TABLE` độc lập, đầy đủ kiểu dữ liệu hiện đại, rằng buộc PRIMARY KEY, FOREIGN KEY ... REFERENCES ..., UNIQUE, NOT NULL, INDEX tối ưu hóa truy vấn.
   - Tuân thủ quy ước đặt tên snake_case cho tên bảng và tên cột.

5. Ma trận Truy vết Yêu cầu (Requirements Traceability Matrix - RTM theo BABOK v3):
   - traceability_matrix: Lập ma trận truy vết toàn diện cho từng yêu cầu chức năng (FR-01, FR-02,...).
   - Mỗi mục (TraceabilityItem) phải bao gồm:
     + req_id: Mã định danh yêu cầu tương ứng (FR-01, FR-02,...).
     + feature_name: Tên tính năng cụ thể.
     + business_rule: Quy tắc nghiệp vụ chi phối tính năng này.
     + related_tables: Danh sách các bảng CSDL liên quan trực tiếp, BẮT BUỘC phải ánh xạ chính xác tên bảng thực tế có trong `sql_ddl_script`.
     + test_scenario_summary: Tóm tắt kịch bản kiểm thử (Test Scenario) trọng tâm dùng để nghiệm thu tính năng.

6. Bộ Kiểm toán Chất lượng Đặc tả & Cảnh báo Điểm Mơ hồ (Quality & Ambiguity Audit):
   - quality_audit:
     + ieee_compliance_score: Chấm điểm từ 0-100 đánh giá mức độ hoàn thiện, chặt chẽ của tài liệu theo chuẩn IEEE 29148.
     + invest_score: Chấm điểm từ 0-100 đánh giá chất lượng User Stories theo bộ tiêu chí INVEST.
     + third_nf_justification: Giải thích chi tiết, thuyết phục tại sao thiết kế cơ sở dữ liệu đã đạt Chuẩn dạng 3 (3NF), nêu rõ cách triệt tiêu phụ thuộc từng phần (2NF) và phụ thuộc bắc cầu (3NF).
     + clarification_questions: Phân tích sâu các lỗ hổng, điểm thiếu sót, thông tin mâu thuẫn hoặc mơ hồ trong biên bản họp thô (Meeting Notes), đưa ra tối thiểu 3-5 câu hỏi nghiệp vụ sắc bén (Elicitation Follow-up Questions) để BA phỏng vấn lại khách hàng/Stakeholders nhằm triệt tiêu rủi ro Scope Creep.

7. Mô hình hóa Sơ đồ Máy Trạng thái (UML State Machine Diagram - stateDiagram-v2):
   - state_machine_entity: Tên thực thể cốt lõi có vòng đời biến đổi trạng thái nghiệp vụ phức tạp nhất trong hệ thống (Ví dụ: "Vòng đời Trạng thái Vé / Chỗ ngồi (Ticket & Seat Lifecycle)" hoặc "Vòng đời Đơn đặt vé (Booking Lifecycle)").
   - state_diagram_mermaid: BẮT BUỘC bắt đầu trực tiếp bằng 'stateDiagram-v2'.
     + Sử dụng `[*]` cho trạng thái bắt đầu (initial) và trạng thái kết thúc (terminal).
     + Nếu tên trạng thái có khoảng trắng hoặc tiếng Việt, khai báo định danh: `state "Tên Trạng Thái" as StateID` (Ví dụ: `state "Đang Giữ Chỗ" as Held`, `state "Đã Thanh Toán" as Confirmed`).
     + Chuyển trạng thái theo cú pháp: `State1 --> State2 : Tên sự kiện kích hoạt` (Ví dụ: `Held --> Confirmed : Thanh toán thành công`).
     + Tuyệt đối KHÔNG chứa dấu chấm phẩy `;` hay ngoặc nhọn `{}` trong nhãn sự kiện.
     + Không chứa thẻ markdown code fence thừa trong chuỗi.

8. Định dạng dữ liệu đầu ra:
   - Toàn bộ dữ liệu trả về phải tuân thủ nghiêm ngặt theo schema JSON của SRSDocument.
"""


def generate_srs_with_telemetry(
    raw_notes: str,
    api_key: str,
    force_refresh: bool = False,
    model_name: str = "gemini-3.8-flash",
) -> Tuple[SRSDocument, TelemetryMetrics]:
    """Phân tích ghi chú họp khách hàng và sinh đặc tả SRS kèm theo telemetry và caching SHA-256.

    Args:
        raw_notes: Nội dung văn bản ghi chú họp khách hàng thô.
        api_key: Khóa API Google Gemini.
        force_refresh: Bỏ qua cache RAM và gọi live Gemini API.
        model_name: Tên model Gemini sử dụng.

    Returns:
        Tuple[SRSDocument, TelemetryMetrics]: Bộ đôi tài liệu SRS và các chỉ số đo lường LLMOps.

    Raises:
        ValueError: Nếu input hoặc API key không hợp lệ.
    """
    if not api_key or not api_key.strip():
        raise ValueError("GEMINI_API_KEY không được để trống. Vui lòng cấu hình API key.")

    if not raw_notes or not raw_notes.strip():
        raise ValueError("Nội dung ghi chú họp khách hàng không được để trống.")

    content_hash = compute_content_hash(raw_notes, model_name=model_name)

    # 1. Kiểm tra Bộ nhớ đệm (Cache Hit)
    if not force_refresh:
        cached_entry = default_srs_cache.get(content_hash)
        if cached_entry:
            cached_doc, original_metrics = cached_entry
            t_start = time.perf_counter()
            doc_copy = cached_doc.model_copy(deep=True)
            lookup_latency_ms = (time.perf_counter() - t_start) * 1000.0
            telemetry = TelemetryMetrics(
                latency_ms=round(lookup_latency_ms, 2),
                prompt_tokens=original_metrics.prompt_tokens,
                completion_tokens=original_metrics.completion_tokens,
                total_tokens=original_metrics.total_tokens,
                cache_hit=True,
                retry_attempts=0,
                content_hash=content_hash,
            )
            return doc_copy, telemetry

    # 2. Gọi Live API với Exponential Backoff Retry
    client = genai.Client(api_key=api_key.strip())
    user_prompt = f"""Dưới đây là biên bản ghi chú họp khách hàng thô (Meeting Notes).
Hãy phân tích nghiệp vụ, chuẩn hóa theo IEEE 29148 & BABOK, thiết kế sơ đồ Sequence, State Machine, ERD 3NF và sinh mã SQL DDL chi tiết:

---
{raw_notes.strip()}
---
"""

    start_time = time.perf_counter()

    def _call_gemini():
        return client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=SRSDocument,
                temperature=0.2,
            ),
        )

    response, retry_attempts = execute_with_exponential_backoff(
        _call_gemini, max_retries=3, base_delay=1.0
    )
    latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    if not response or not response.text:
        raise ValueError("Không nhận được phản hồi hợp lệ từ mô hình AI.")

    # 3. Trích xuất token usage từ metadata hoặc ước lượng fallback
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
        completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
        total_tokens = getattr(response.usage_metadata, "total_token_count", 0) or 0

    if not total_tokens:
        prompt_tokens = max(1, len(user_prompt) // 4)
        completion_tokens = max(1, len(response.text) // 4)
        total_tokens = prompt_tokens + completion_tokens

    # 4. Parse JSON sang Pydantic Model
    doc: SRSDocument = SRSDocument.model_validate_json(response.text)

    # 5. Tiền xử lý và làm sạch cú pháp Mermaid
    try:
        doc.sequence_diagram_mermaid = clean_and_validate_mermaid(
            doc.sequence_diagram_mermaid, diagram_type="sequenceDiagram"
        )
    except Exception:
        pass

    try:
        doc.er_diagram_mermaid = clean_and_validate_mermaid(
            doc.er_diagram_mermaid, diagram_type="erDiagram"
        )
    except Exception:
        pass

    try:
        if getattr(doc, "state_diagram_mermaid", ""):
            doc.state_diagram_mermaid = clean_and_validate_mermaid(
                doc.state_diagram_mermaid, diagram_type="stateDiagram-v2"
            )
    except Exception:
        pass

    telemetry = TelemetryMetrics(
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cache_hit=False,
        retry_attempts=retry_attempts,
        content_hash=content_hash,
    )

    # Lưu vào bộ nhớ đệm
    default_srs_cache.set(content_hash, doc.model_copy(deep=True), telemetry)

    return doc, telemetry


def generate_srs_from_notes(raw_notes: str, api_key: str) -> SRSDocument:
    """Phân tích ghi chú họp khách hàng và sinh đặc tả SRS (Hàm tương thích ngược).

    Args:
        raw_notes: Nội dung văn bản ghi chú họp khách hàng thô.
        api_key: Khóa API Google Gemini.

    Returns:
        SRSDocument: Đối tượng Pydantic chứa toàn bộ thông tin đặc tả hệ thống.
    """
    doc, _ = generate_srs_with_telemetry(raw_notes, api_key)
    return doc
