---
name: ui-critique
description: Thang chấm điểm 1-5 theo 8 tiêu chí chuẩn mực thiết kế UI/UX, quy trình kiểm định ảnh chụp thực tế và phát hiện khiếm khuyết giao diện.
---

# UI Critique — Thang Chấm Điểm & Quy Trình Kiểm Định Giao Diện

Kỹ năng này cung cấp quy chuẩn đánh giá nghiêm ngặt cho mọi màn hình giao diện trong `ba-srs-uml-copilot`. Mọi đề xuất cải tiến hoặc thay đổi giao diện từ các công cụ hỗ trợ khác (bao gồm cả `ui-ux-pro-max`) bắt buộc phải vượt qua bài kiểm tra của kỹ năng này trước khi chấp thuận áp dụng.

---

## 1. Thang Điểm 8 Tiêu Chí Thiết Kế (1 đến 5 điểm)

Mỗi tiêu chí được chấm theo thang điểm từ 1 đến 5 (1: Không thể chấp nhận, 2: Kém, 3: Tạm chấp nhận, 4: Tốt / Chuyên nghiệp, 5: Xuất sắc / Hoàn hảo):

| # | Tiêu Chí Đánh Giá | Mô Tả & Điều Kiện Đạt Điểm Cao (>= 4) |
| :-: | :--- | :--- |
| **1** | **Thứ bậc thị giác (Visual Hierarchy)** | Người dùng dễ dàng nhận ra đâu là hành động chính (Primary Action), đâu là nội dung cốt lõi; nút bấm hành động dùng màu thương hiệu chuẩn xác, không dùng màu báo động (đỏ) cho tác vụ thông thường. Tiêu đề phân cấp rành mạch (h1 > h2 > h3). |
| **2** | **Khoảng cách & Căn lề (Spacing & Alignment)** | Toàn bộ khoảng cách tuân thủ nghiêm ngặt thang tỷ lệ 4/8/16/24/32px; lề và đệm của các container, thẻ card, danh sách đồng nhất theo trục thẳng hàng; không có hiện tượng thụt lề so le hay xô lệch. |
| **3** | **Màu sắc & Độ tương phản (Color & Contrast)** | Đạt tiêu chuẩn **WCAG AA** (tỷ lệ tương phản chữ/nền >= 4.5:1 cho văn bản thường, >= 3:1 cho tiêu đề lớn và biểu tượng). Không xảy ra lỗi chữ sáng trên nền sáng (ví dụ: chữ vàng trên nền vàng) hoặc chữ đen trên nền xám tối. Bảng màu tuân thủ 1 màu nhấn + bảng trung tính + 3 màu ngữ nghĩa. |
| **4** | **Chữ & Dấu tiếng Việt (Typography & Diacritics)** | Font chữ hỗ trợ 100% tiếng Việt, các ký tự có dấu không bị nhảy font (fallback glitch); line-height cân đối (1.4 – 1.6); không bị ngắt đôi từ vô lý trên màn hình hẹp (ví dụ: "Cinema \n Booking"). |
| **5** | **Nhất quán thành phần (Component Consistency)** | Các nút bấm, thẻ chỉ số (KPI Card), huy hiệu trạng thái (Badge), bảng dữ liệu đều tái sử dụng chung định dạng từ `components.py` và `tokens.py`. Bo góc (radius), độ đổ bóng (shadow) và kiểu viền đồng nhất trên toàn ứng dụng. |
| **6** | **Mật độ thông tin & Tiết lộ dần (Progressive Disclosure)** | Không làm người dùng nghiệp vụ (BA/PM) bị ngợp bởi các chi tiết kỹ thuật chuyên sâu (LLM latency, cache hash, token breakdown, SQLite engine log). Dữ liệu nâng cao được thu gọn thông minh trong expander/drawer; nhãn tab ngắn gọn (< 20 ký tự), không làm tràn thanh điều hướng. |
| **7** | **Phản hồi trạng thái (State Feedback)** | Thể hiện trực quan, rõ ràng cả 4 trạng thái: Trống (Empty State có thẻ gợi ý 1-click), Đang tải (Loading/Spinner thân thiện), Lỗi (Error Message rõ nguyên nhân và cách khắc phục), Thành công (Success/Toast rõ ràng). |
| **8** | **Responsive & Khả năng tiếp cận (Responsive & A11y)** | Giao diện co giãn mượt mà từ màn hình lớn (1440px) đến màn hình hẹp di động (~400px) mà không bị vỡ bố cục, không tràn ngang ngoài ý muốn; các nút bấm có kích thước chạm tối thiểu 40x40px; hiển thị focus ring rõ ràng khi duyệt bằng bàn phím. |

---

## 2. Quy Trình Đánh Giá (Critique Workflow)

1. **Thu thập ảnh chụp thực tế**:
   - Sử dụng ảnh chụp màn hình từ `docs/ui-audit/<mốc_thời_gian>/` (tuyệt đối không đánh giá chỉ qua tưởng tượng hoặc đọc mã nguồn).
2. **Chấm điểm từng tiêu chí**:
   - Ghi điểm chi tiết từ 1 đến 5 cho từng mục trong 8 tiêu chí.
3. **Lập danh sách lỗi & Phân loại mức độ**:
   - **Nghiêm trọng (Critical)**: Vi phạm tương phản WCAG (< 3:1), vỡ bố cục hoàn toàn, chữ không đọc được, nút bấm sai ngữ nghĩa gây nhầm lẫn.
   - **Trung bình (Moderate)**: Khoảng cách lệch chuẩn, tiêu đề tab bị tràn sinh nút cuộn, thiếu empty state hấp dẫn.
   - **Nhỏ (Minor)**: Lệch 2-4px căn lề, biểu tượng chưa đồng bộ 100%, câu từ tiếng Việt chưa gãy gọn.
4. **Đề xuất giải pháp sửa chữa cụ thể**:
   - Nêu rõ file cần sửa (`tokens.py`, `styles.py`, `components.py` hoặc tệp tab tương ứng).

---

## 3. Ngưỡng Nghiệm Thu Bắt Buộc (Pass Threshold)

> **Điều kiện đạt yêu cầu**:
> - Tổng điểm trung bình $\ge 4.2 / 5.0$.
> - **KHÔNG ĐƯỢC CÓ BẤT KỲ TIÊU CHÍ NÀO DƯỚI 4 ĐIỂM**.
> - Nếu còn bất kỳ tiêu chí nào dưới 4 điểm $\rightarrow$ Trạng thái: **REJECTED**, bắt buộc quay lại vòng lặp `/redesign`.
