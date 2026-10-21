---
name: ux-writing-vi
description: Quy chuẩn văn phong tiếng Việt trong thiết kế giao diện phần mềm nghiệp vụ (BA/PM), đặt nhãn nút, thông báo lỗi, empty state và từ điển thuật ngữ.
---

# UX Writing Tiếng Việt — Hướng Dẫn Soạn Thảo Giao Diện Nghiệp Vụ

Kỹ năng này chuẩn hóa toàn bộ ngôn ngữ hiển thị trên giao diện của `ba-srs-uml-copilot`. Đối tượng người dùng mục tiêu là các **Business Analyst (BA), Product Manager (PM), Solution Architect (SA) và Developer tại Việt Nam**.

---

## 1. Nguyên Tắc Văn Phong Cốt Lõi

1. **Ngắn gọn & Trực diện**:
   - Loại bỏ các từ thừa, từ đệm ("Xin vui lòng", "Bạn có thể tiến hành...").
   - Vào thẳng bản chất: `Phân tích yêu cầu` thay vì `Bấm vào đây để hệ thống tiến hành phân tích nội dung ghi chú họp`.
2. **Thân thiện nhưng Chuẩn mực Chuyên nghiệp (B2B SaaS)**:
   - Dùng đại từ xưng hô tôn trọng, trung tính, tích cực.
   - Tránh văn phong cộc lốc hoặc quá máy móc mang tính mã lệnh.
3. **Nhãn nút bấm luôn là ĐỘNG TỪ hành động**:
   - Nút hành động phải diễn tả rõ kết quả người dùng sẽ nhận được khi nhấn:
     - Đúng: `Phân tích Yêu cầu`, `Nạp Kịch bản Mẫu`, `Tải trọn bộ Hồ sơ (.ZIP)`, `Tự động Đồng bộ Bảng`, `Lưu Thay đổi`.
     - Sai: `Gửi`, `Thực hiện`, `Bấm vào đây`, `Kịch bản`, `OK`.

---

## 2. Tiêu Chuẩn Thông Báo Lỗi (Error Message Anatomy)

Mọi thông báo lỗi phải tuân thủ công thức **2 thành phần**:
$$\text{Thông báo Lỗi} = \text{[Chuyện gì đã xảy ra]} + \text{[Người dùng cần làm gì để khắc phục]}$$

1. **Không làm lộ chi tiết kỹ thuật thô hoặc stack trace**:
   - Tuyệt đối không in nguyên văn `KeyError: 'tables'`, `500 Internal Server Error`, `ConnectionRefusedError`.
2. **Ví dụ đối chiếu**:
   - Sai: `Lỗi: GEMINI_API_KEY is not set or invalid token.`
   - Đúng: `Chưa kết nối Gemini API. Vui lòng nhập API Key ở thanh bên trái hoặc cấu hình biến môi trường GEMINI_API_KEY để tiếp tục.`
   - Sai: `Validation error: Notes empty.`
   - Đúng: `Chưa có nội dung ghi chú họp. Vui lòng dán biên bản họp hoặc chọn một kịch bản mẫu bên dưới để bắt đầu.`
   - Sai: `PayloadTooLarge: String length > 50000.`
   - Đúng: `Nội dung ghi chú họp vượt quá giới hạn xử lý (50.000 ký tự). Bạn hãy chia nhỏ nội dung theo từng module nghiệp vụ để phân tích chính xác nhất.`

---

## 3. Tiêu Chuẩn Trạng Thái Ban Đầu (Empty State Copy)

Khi người dùng mở ứng dụng lần đầu và chưa có dữ liệu:
- **Tiêu đề chào đón**: Nêu rõ giá trị của công cụ: `Chuyển hóa Ghi chú Họp thành Đặc tả Phần mềm Chuẩn mực`.
- **Mô tả ngắn**: `Chỉ cần dán biên bản thảo luận nghiệp vụ thô, AI Copilot sẽ tự động trích xuất User Stories, mô hình hoá UML và thiết kế CSDL 3NF.`
- **Hướng dẫn bước đầu (1-Click Action)**: Cung cấp các thẻ chọn nhanh kịch bản mẫu:
  - `🎬 Đặt vé Xem phim (Cinema Booking)` — Nghiệp vụ khóa ghế thời gian thực, giữ chỗ và thanh toán.
  - `🚌 Đặt vé Xe khách Liên tỉnh (Bus Ticketing)` — Tuyến đường, phụ phí và quản lý số ghế.
  - `📦 Quản lý Kho Hàng (WMS)` — Nhập, xuất, kiểm kê vị trí kệ hàng và tồn kho.

---

## 4. Bảng Thuật Ngữ Nghiệp Vụ Chuẩn Hóa (Glossary of Terms)

Để giữ tính chuyên môn cao cho BA/PM, các thuật ngữ quốc tế chuyên ngành được giữ nguyên hoặc kèm giải nghĩa tiếng Việt chuẩn xác:

| Thuật Ngữ Gốc | Thuật Ngữ Tiếng Việt Chuẩn Hóa Trên UI | Giải Thích Ngắn Gọn |
| :--- | :--- | :--- |
| **SRS** | Đặc tả Yêu cầu Phần mềm (SRS) | Software Requirements Specification (IEEE 29148) |
| **User Story** | Yêu cầu Dạng User Story | Định dạng "Là một... Tôi muốn... Để..." |
| **Acceptance Criteria (AC)** | Tiêu chí Nghiệm thu BDD (Given-When-Then) | Kịch bản kiểm thử hành vi BDD Gherkin |
| **RTM** | Ma trận Truy vết Yêu cầu (RTM) | Requirements Traceability Matrix (BABOK v3) |
| **Sequence Diagram** | Sơ đồ Tuần tự Nghiệp vụ | Minh hoạ luồng tương tác giữa các tác nhân |
| **State Machine** | Sơ đồ Máy Trạng thái | Vòng đời và trạng thái của thực thể trung tâm |
| **ERD 3NF** | Sơ đồ Thực thể Quan hệ Chuẩn 3NF | Triệt tiêu phụ thuộc từng phần & bắc cầu |
| **DDL Script** | Kịch bản Khởi tạo CSDL Vật lý | Các câu lệnh SQL `CREATE TABLE`, `INDEX` |
| **UAT Scenario** | Kịch bản Kiểm thử Chấp nhận (UAT) | Kịch bản bàn giao và nghiệm thu với khách hàng |
| **Telemetry / LLMOps** | Giám sát Vận hành Mô hình | Độ trễ (ms), lượng Token và mã băm SHA-256 |
