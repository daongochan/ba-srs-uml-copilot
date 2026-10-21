# /design-audit — Quy Trình Khảo Sát & Đánh Giá Giao Diện Tự Động

Quy trình này tự động chụp ảnh thực tế ứng dụng Streamlit, áp dụng thang điểm `ui-critique` (8 tiêu chí) và lập báo cáo phân loại khiếm khuyết.

---

## Điều kiện kích hoạt (Trigger)
- Người dùng gõ lệnh `/design-audit` hoặc yêu cầu rà soát, đánh giá hiện trạng giao diện.

---

## Bước 1: Khởi Động Ứng Dụng & Kiểm Tra Cổng Mạng
1. Xác định ứng dụng Streamlit đang chạy trên cổng nào (mặc định 8501 / 8503):
   ```powershell
   Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -ge 8500 -and $_.LocalPort -le 8510 }
   ```
2. Nếu chưa chạy, khởi động ở chế độ nền:
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run src/app.py --server.port 8501 --server.headless true
   ```

---

## Bước 2: Chụp Ảnh Toàn Diện Các Trạng Thái Chuẩn
1. Tạo thư mục lưu trữ ảnh theo mốc thời gian:
   ```powershell
   $today = Get-Date -Format "yyyy-MM-dd"
   New-Item -ItemType Directory -Force -Path "docs/ui-audit/$today"
   ```
2. Thực thi kịch bản chụp ảnh tự động (`scratch/capture.js`):
   - Màn hình trống ban đầu (`01_initial_state.png`).
   - Trạng thái báo lỗi người dùng (`02_error_state.png`).
   - Trạng thái nạp kịch bản mẫu (`03_sample_loaded.png`).
   - 4 tab kết quả nghiệp vụ (`04_tab_1_srs.png`, `04_tab_2_uml.png`, `04_tab_3_erd.png`, `04_tab_4_export.png`).
   - Màn hình hẹp di động 400px (`05_mobile_400px.png`).

---

## Bước 3: Đánh Giá & Chấm Điểm Theo Kỹ Năng `ui-critique`
1. Đọc từng ảnh chụp và chấm điểm từ 1 đến 5 cho 8 tiêu chí:
   - (1) Thứ bậc thị giác
   - (2) Khoảng cách & Căn lề
   - (3) Màu sắc & Độ tương phản (WCAG AA >= 4.5:1)
   - (4) Chữ & Dấu tiếng Việt
   - (5) Nhất quán thành phần
   - (6) Mật độ thông tin & Tiết lộ dần
   - (7) Phản hồi trạng thái
   - (8) Responsive & Khả năng tiếp cận
2. Phân loại lỗi tìm được theo 3 mức độ:
   - **Nghiêm trọng (Critical)**: Vỡ layout, chữ không đọc được, vi phạm tương phản WCAG.
   - **Trung bình (Moderate)**: Tiêu đề tràn cuộn, khoảng cách xô lệch, thiếu empty state.
   - **Nhỏ (Minor)**: Lệch 2-4px, dùng emoji thay vì SVG icon, câu từ chưa gãy gọn.

---

## Bước 4: Lập Báo Cáo & Khuyến Nghị
1. Xuất bảng điểm so sánh trực quan.
2. Nêu rõ các tệp cần can thiệp (`src/ui/tokens.py`, `src/ui/styles.py`, `src/ui/components.py`,...).
3. Nếu điểm bất kỳ tiêu chí nào < 4.0, kích hoạt workflow `/redesign <tên màn hình>`.
