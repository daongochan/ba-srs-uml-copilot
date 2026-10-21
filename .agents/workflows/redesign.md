# /redesign — Quy Trình Tái Thiết Kế & Hoàn Thiện Màn Hình Theo Vòng Lặp

Quy trình này hướng dẫn tái thiết kế từng màn hình cụ thể theo chu trình lặp: Đọc brief ➔ Phác thảo Layout ➔ Triển khai code ➔ Chạy app & Chụp ảnh thật ➔ Chấm điểm theo `ui-critique` ➔ Tinh chỉnh sửa lỗi (Tối đa 3 vòng lặp).

---

## Cú pháp kích hoạt (Trigger)
- Người dùng gõ lệnh: `/redesign <tên_màn_hình>`
- Ví dụ:
  - `/redesign input-and-header`
  - `/redesign tab-srs`
  - `/redesign tab-dynamic-models`
  - `/redesign tab-database-erd`
  - `/redesign tab-export`

---

## Vòng lặp Tái thiết kế (Tối đa 3 Vòng / Màn hình)

```
[BƯỚC 1: ĐỌC BRIEF & PHÁC THẢO LAYOUT]
                 │
                 ▼
[BƯỚC 2: TRIỂN KHAI CODE GIAO DIỆN CÓ KỶ LUẬT]
                 │
                 ▼
[BƯỚC 3: KIỂM THỬ MÃ NGUỒN (Pytest + Ruff)]
                 │
                 ▼
[BƯỚC 4: CHỤP ẢNH MÀN HÌNH THỰC TẾ (Visual QA)]
                 │
                 ▼
[BƯỚC 5: CHẤM ĐIỂM THEO UI-CRITIQUE (8 Tiêu chí)]
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
Đạt (Mọi tiêu chí >= 4)    Chưa Đạt (< 4 điểm)
    │                         │
    │                   Số vòng < 3 ?
    │                   ├── CÓ  ➔ Quay lại Bước 2 để sửa lỗi
    │                   └── KHÔNG ➔ DỪNG LẠI và hỏi ý kiến người dùng
    ▼
Hoàn thành màn hình ➔ Mở PR kèm ảnh Trước/Sau
```

---

## Chi Tiết Các Bước

### Bước 1: Đọc Brief & Phác Thảo Bố Cục (Wireframe Sketch)
1. Xác định rõ mục tiêu của màn hình, đối tượng người dùng (BA/PM), thông tin chính cần nhấn mạnh.
2. Viết bản phác thảo ngắn (Ascii/Markdown wireframe) mô tả luồng mắt nhìn từ trên xuống dưới.
3. Đối chiếu Design Tokens (`src/ui/tokens.py`) để chọn màu, font và khoảng cách chuẩn.

### Bước 2: Triển Khai Code Giao Diện Có Kỷ Luật
1. Không sửa đổi logic trong `src/services/`, `src/validators/`, `src/models/`.
2. Sử dụng các hàm dựng sẵn trong `src/ui/components.py` hoặc tạo component mới nếu cần tái sử dụng.
3. Hạn chế CSS nội dòng; chỉ bổ sung CSS có ngữ nghĩa trong `src/ui/styles.py`.

### Bước 3: Kiểm Thử Mã Nguồn & Định Dạng
1. Chạy linter:
   ```powershell
   .\.venv\Scripts\python.exe -m ruff check .
   .\.venv\Scripts\python.exe -m ruff format --check .
   ```
2. Chạy unit tests:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest tests/test_ui_theme.py tests/test_ui_modular_tabs.py -v
   ```
   *Quy tắc cứng: 100% tests phải Pass.*

### Bước 4: Chạy App & Chụp Ảnh Thực Tế
1. Chạy kịch bản chụp ảnh màn hình đã sửa (`scratch/capture.js`).
2. Lưu ảnh mới vào thư mục tương ứng trong `docs/ui-audit/`.

### Bước 5: Chấm Điểm & Đánh Giá
1. Tự động áp dụng 8 tiêu chí `ui-critique`.
2. Nếu mọi tiêu chí đạt $\ge 4.0$: Đạt yêu cầu ➔ Chuẩn bị commit.
3. Nếu còn tiêu chí $< 4.0$:
   - Nếu chưa đủ 3 vòng: Thực hiện sửa chữa ngay lập tức tại Bước 2.
   - Nếu đã qua 3 vòng lặp mà vẫn chưa đạt: **DỪNG LẠI**, tổng hợp các điểm nghẽn và hỏi người dùng phương hướng giải quyết.
