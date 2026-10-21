---
name: visual-qa
description: Quy trình tự động hóa kiểm định trực quan (Visual QA), chạy ứng dụng Streamlit, chụp ảnh các trạng thái chuẩn và so sánh trước sau.
---

# Visual QA — Quy Trình Kiểm Thử Trực Quan & Xác Minh Giao Diện

Kỹ năng này bảo đảm nguyên tắc bất biến: **"Mọi thay đổi giao diện phải được xác minh bằng ảnh chụp màn hình thật. Không có ảnh thì không báo hoàn thành."**

---

## 1. Danh Mục Trạng Thái Màn Hình Bắt Buộc Chụp (Standard States)

Mỗi lần kiểm định hoặc tái thiết kế một màn hình, kỹ sư phải thu thập đủ 8 trạng thái trực quan:

| Mã Ảnh | Trạng Thái Cần Chụp | Kích Thước Viewport | Mục Đích Kiểm Tra |
| :---: | :--- | :---: | :--- |
| `01_initial_state.png` | Màn hình ban đầu khi mở app | 1440 x 1000 | Kiểm tra Empty State, Hero Banner, các gợi ý kịch bản mẫu. |
| `02_error_state.png` | Trạng thái báo lỗi người dùng | 1440 x 1000 | Kiểm tra màu sắc hộp thoại lỗi, ngữ nghĩa nút bấm và văn phong tiếng Việt. |
| `03_sample_loaded.png` | Đã nạp kịch bản khảo sát mẫu | 1440 x 1000 | Kiểm tra khung nhập text, bộ đếm ký tự và tương phản màu sắc. |
| `04_tab_1_srs.png` | Tab 1: Đặc tả Yêu cầu SRS | 1440 x 1100 | Kiểm tra Bento KPI cards, User Story cards, bảng RTM, cảnh báo Linter. |
| `04_tab_2_uml.png` | Tab 2: Sơ đồ Tuần tự & State | 1440 x 1100 | Kiểm tra thanh công cụ pan/zoom Mermaid, kích thước font chữ sơ đồ. |
| `04_tab_3_erd.png` | Tab 3: Thiết kế CSDL 3NF | 1440 x 1100 | Kiểm tra sơ đồ ERD toàn màn hình, thanh sub-nav 3 chế độ xem. |
| `04_tab_4_export.png` | Tab 4: Xuất Bản Hồ Sơ | 1440 x 1100 | Kiểm tra hệ thống 4 nút tải file (Primary/Secondary), khung xem trước. |
| `05_mobile_400px.png` | Màn hình hẹp di động | 400 x 900 | Kiểm tra Responsive, không gãy từ, không tràn ngang, thanh điều hướng gập gọn. |

---

## 2. Quy Chuẩn Lưu Trữ Thư Mục (`docs/ui-audit/`)

Ảnh chụp được phân loại theo cấu trúc thời gian và phiên bản:
```
docs/ui-audit/
├── before/                 # Mốc khảo sát ban đầu trước khi cải tổ (Giai đoạn 0)
├── 2026-10-21/             # Thư mục theo ngày thực hiện
│   ├── step1-tokens/       # Ảnh kiểm tra bước hoàn thành Design Tokens & Theme
│   ├── step2-input/        # Ảnh kiểm tra màn hình nhập liệu & kịch bản mẫu
│   └── step3-tabs/         # Ảnh kiểm tra 4 tab nghiệp vụ
└── comparisons/            # Ảnh ghép so sánh Before / After phục vụ mở PR
```

---

## 3. Công Cụ & Kịch Bản Chụp Ảnh Tự Động

- Ưu tiên sử dụng kịch bản Node.js Puppeteer Core (`scratch/capture.js`) kết nối trực tiếp đến trình duyệt Google Chrome / Microsoft Edge có sẵn trên máy người dùng, hoặc sử dụng Playwright / browser tools.
- Tham số truy cập chế độ Demo Visual Testing: `http://localhost:8501/?demo=1` (cho phép Streamlit nạp sẵn dữ liệu mẫu để render toàn bộ 4 tab mà không cần gọi API thật).

---

## 4. Danh Mục Kiểm Tra Trực Quan Trước Khi Đóng Task (Pre-flight Checklist)

- [ ] **Tương phản WCAG AA**: Không có bất kỳ dòng chữ nào có tỷ lệ tương phản dưới 4.5:1 (đặc biệt các thẻ cảnh báo vàng, cam).
- [ ] **Dấu tiếng Việt**: Các chữ như `Đặc tả`, `Thực thể`, `Khởi tạo`, `Biên bản` hiển thị đồng bộ một font, không bị lỗi font nhảy cóc (glitch).
- [ ] **Không tràn lề ngang**: Ở màn hình 400px, toàn bộ nội dung nằm gọn trong viewport, thanh cuộn ngang không xuất hiện ngoài ý muốn.
- [ ] **Trạng thái Hover/Focus**: Các nút bấm có hiệu ứng đổi màu rõ ràng khi trỏ chuột và có viền focus xanh/indigo khi duyệt bằng phím Tab.
- [ ] **Đính kèm ảnh minh chứng vào PR**: Mọi PR phải có ít nhất 1 cặp ảnh Trước / Sau chứng minh cải tiến đạt chuẩn.
