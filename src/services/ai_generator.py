"""AI Generation service using Google GenAI SDK to produce structured SRS documents."""

import json
from google import genai
from google.genai import types

from src.models.srs_schema import SRSDocument
from src.validators.syntax_validator import clean_and_validate_mermaid, validate_sql_ddl

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

5. Định dạng dữ liệu đầu ra:
   - Toàn bộ dữ liệu trả về phải tuân thủ nghiêm ngặt theo schema JSON của SRSDocument.
"""


def generate_srs_from_notes(raw_notes: str, api_key: str) -> SRSDocument:
    """Phân tích ghi chú họp khách hàng và sinh đặc tả SRS, sơ đồ UML và SQL DDL

    sử dụng model gemini-3.8-flash với cơ chế ép kiểu Structured Output.

    Args:
        raw_notes: Nội dung văn bản ghi chú họp khách hàng thô.
        api_key: Khóa API Google Gemini.

    Returns:
        SRSDocument: Đối tượng Pydantic chứa toàn bộ thông tin đặc tả hệ thống.

    Raises:
        ValueError: Nếu nội dung đầu vào hoặc API key trống, hoặc kết quả sinh lỗi.
    """
    if not api_key or not api_key.strip():
        raise ValueError("GEMINI_API_KEY không được để trống. Vui lòng cấu hình API key.")

    if not raw_notes or not raw_notes.strip():
        raise ValueError("Nội dung ghi chú họp khách hàng không được để trống.")

    client = genai.Client(api_key=api_key.strip())

    user_prompt = f"""Dưới đây là biên bản ghi chú họp khách hàng thô (Meeting Notes).
Hãy phân tích nghiệp vụ, chuẩn hóa theo IEEE 29148 & BABOK, thiết kế sơ đồ Sequence, ERD 3NF và sinh mã SQL DDL chi tiết:

---
{raw_notes.strip()}
---
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=SRSDocument,
            temperature=0.2,
        ),
    )

    if not response or not response.text:
        raise ValueError("Không nhận được phản hồi hợp lệ từ mô hình AI.")

    # Parse JSON sang Pydantic Model
    doc: SRSDocument = SRSDocument.model_validate_json(response.text)

    # Tiền xử lý và làm sạch cú pháp Mermaid nếu có thẻ markdown bọc ngoài
    try:
        doc.sequence_diagram_mermaid = clean_and_validate_mermaid(
            doc.sequence_diagram_mermaid, diagram_type="sequenceDiagram"
        )
    except Exception:
        # Nếu validator phát hiện lỗi nhẹ, giữ nguyên hoặc cố gắng chuẩn hóa
        pass

    try:
        doc.er_diagram_mermaid = clean_and_validate_mermaid(
            doc.er_diagram_mermaid, diagram_type="erDiagram"
        )
    except Exception:
        pass

    return doc
