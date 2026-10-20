"""SRS Data Models and Schemas based on IEEE 29148 and BABOK standards."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AcceptanceCriterion(BaseModel):
    """Given-When-Then acceptance criterion structure."""

    given: str = Field(
        ...,
        description="Tiền điều kiện hoặc ngữ cảnh ban đầu (Given: Context/Precondition)",
    )
    when: str = Field(
        ...,
        description="Hành động hoặc sự kiện kích hoạt từ phía tác nhân hoặc hệ thống (When: Action/Trigger)",
    )
    then: str = Field(
        ...,
        description="Kết quả mong đợi hoặc trạng thái sau hành động (Then: Expected Outcome)",
    )


class FunctionalRequirement(BaseModel):
    """Functional Requirement (FR) specification with User Story and Acceptance Criteria."""

    req_id: str = Field(
        ...,
        description="Mã định danh yêu cầu chuẩn (ví dụ: FR-01, FR-02)",
    )
    title: str = Field(
        ...,
        description="Tiêu đề ngắn gọn mô tả chức năng",
    )
    user_story: str = Field(
        ...,
        description="User story theo định dạng: Là [tác nhân], tôi muốn [hành động], để [mục đích]",
    )
    priority: Literal["High", "Medium", "Low", "Must Have", "Should Have", "Could Have", "Won't Have"] = Field(
        default="High",
        description="Mức độ ưu tiên theo chuẩn MoSCoW hoặc High/Medium/Low",
    )
    acceptance_criteria: List[AcceptanceCriterion] = Field(
        default_factory=list,
        description="Danh sách các kịch bản tiêu chí chấp nhận (Acceptance Criteria)",
    )


class NonFunctionalRequirement(BaseModel):
    """Non-Functional Requirement (NFR) specification."""

    category: str = Field(
        ...,
        description="Nhóm yêu cầu phi chức năng (Security, Performance, Reliability, Usability, Scalability, v.v.)",
    )
    description: str = Field(
        ...,
        description="Mô tả chi tiết yêu cầu phi chức năng theo chuẩn IEEE 29148",
    )
    metric: str = Field(
        ...,
        description="Chỉ số đo lường định lượng và tiêu chuẩn nghiệm thu (SLA/KPI/Response Time/Threshold)",
    )


class SRSDocument(BaseModel):
    """Software Requirements Specification (SRS) Document combining BABOK & IEEE 29148."""

    project_title: str = Field(
        ...,
        description="Tên dự án phần mềm",
    )
    business_objective: str = Field(
        ...,
        description="Mục tiêu kinh doanh cốt lõi (Business Objective & Scope)",
    )
    actors: List[str] = Field(
        default_factory=list,
        description="Danh sách tác nhân (Actors / Roles) tương tác với hệ thống",
    )
    functional_requirements: List[FunctionalRequirement] = Field(
        default_factory=list,
        description="Danh sách các yêu cầu chức năng",
    )
    non_functional_requirements: List[NonFunctionalRequirement] = Field(
        default_factory=list,
        description="Danh sách các yêu cầu phi chức năng",
    )
    sequence_diagram_mermaid: str = Field(
        ...,
        description=(
            "Mã nguồn sơ đồ tuần tự Mermaid (Sequence Diagram) minh họa luồng nghiệp vụ trọng tâm. "
            "Bắt buộc bắt đầu bằng 'sequenceDiagram'. "
            "Mọi participant phải khai báo ID tiếng Anh viết liền và đặt tên tiếng Việt trong ngoặc kép (VD: participant U as \"Khach Hang\"). "
            "Nội dung thông điệp sau dấu hai chấm ':' không được chứa dấu chấm phẩy ';' hay ngoặc nhọn '{}'."
        ),
    )
    er_diagram_mermaid: str = Field(
        ...,
        description=(
            "Mã nguồn sơ đồ thực thể quan hệ Mermaid (Entity Relationship Diagram - 3NF). "
            "Bắt buộc bắt đầu bằng 'erDiagram'. "
            "Tên bảng chỉ dùng chữ cái tiếng Anh và dấu gạch dưới. "
            "Bên trong khối '{ }', mỗi dòng chỉ gồm: <type> <attribute_name> <PK/FK> \"<comment>\" "
            "(Tuyệt đối KHÔNG viết varchar(50) mà chỉ viết varchar, KHÔNG có dấu phẩy cuối dòng, comment bắt buộc bọc trong dấu ngoặc kép \"\")."
        ),
    )
    sql_ddl_script: str = Field(
        ...,
        description="Mã SQL DDL (Data Definition Language) khởi tạo bảng và khóa ngoại chuẩn 3NF",
    )
