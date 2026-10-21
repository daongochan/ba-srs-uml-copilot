# /ui-polish — Lượt Rà Soát & Tinh Chỉnh Giao Diện Cuối Cùng (Final Polish)

Quy trình này thực hiện đợt tổng kiểm tra vi mô (Micro-interactions, căn lề pixel, trạng thái hover/focus, văn phong tiếng Việt và khả năng co giãn trên màn hình hẹp) trước khi nghiệm thu hoàn tất.

---

## Điều kiện kích hoạt (Trigger)
- Người dùng gõ lệnh `/ui-polish` hoặc trước khi tạo Pull Request tổng kết giao diện.

---

## Danh Mục 5 Điểm Rà Soát Trọng Tâm (5-Point Polish Checklist)

### 1. Căn Lề & Khoảng Cách Vi Mô (Pixel & Alignment)
- [ ] Mọi khoảng cách padding/margin giữa các card, container, tiêu đề tuân thủ đúng thang 4/8/16/24/32px.
- [ ] Không có phần tử nào bị lệch 1-2px so với trục căn lề dọc của toàn trang.
- [ ] Các icon và nhãn chữ đi kèm được căn giữa chuẩn xác (`align-items: center`, `gap: 8px`).

### 2. Trạng Thái Tương Tác (Hover, Active & Focus Rings)
- [ ] Các nút bấm (Primary, Secondary, Outline) đổi màu dịu mắt khi hover (`transition: all 0.15s ease`).
- [ ] Hiển thị rõ viền nét Focus Ring (`outline: 2px solid #4F46E5`, `outline-offset: 2px`) khi người dùng duyệt bằng phím Tab.
- [ ] Con trỏ chuột chuyển thành hình bàn tay (`cursor: pointer`) trên tất cả các thành phần có thể tương tác (Buttons, Tabs, Radio, Cards).

### 3. Chuẩn Hóa Văn Phong Tiếng Việt (UX Copy & Diacritics)
- [ ] Tất cả nhãn nút bấm bắt đầu bằng **động từ hành động** (`Phân tích`, `Nạp`, `Tải`, `Lưu`).
- [ ] Thông báo lỗi tuân thủ công thức: `[Chuyện gì xảy ra] + [Cách khắc phục]`.
- [ ] Không còn bất kỳ từ ngữ mơ hồ, tiếng lóng lập trình thô hoặc stack trace lộ ra giao diện.
- [ ] Các từ chuyên ngành BA (SRS, RTM, INVEST, BDD, 3NF) được giải nghĩa rõ ràng.

### 4. Độ Tương Phản Màu Sắc (WCAG AA Compliance)
- [ ] Kiểm tra toàn bộ các khối màu:
  - Text thường trên nền: Contrast ratio $\ge 4.5:1$.
  - Text lớn / Tiêu đề / Icon trên nền: Contrast ratio $\ge 3:1$.
- [ ] Không còn bất kỳ vùng nào dùng chữ vàng trên nền vàng chanh hoặc chữ xám mờ trên nền xám.

### 5. Kiểm Thử Màn Hình Hẹp Di Động (~400px Viewport)
- [ ] Chạy viewport 400x900px:
  - Không xuất hiện thanh cuộn ngang toàn trang.
  - Tiêu đề dự án và tiêu đề tab không bị gãy đôi từ.
  - Bento KPI Grid tự động chuyển sang bố cục 1 hoặc 2 cột mượt mà.
  - Các nút tải file xếp chồng dọc tự nhiên, không bị cụt mép.

---

## Các Lệnh Thực Thi Kiểm Tra
```powershell
# 1. Chạy linter & format code
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .

# 2. Chạy toàn bộ test suite
.\.venv\Scripts\python.exe -m pytest

# 3. Chụp ảnh nghiệm thu lần cuối
node scratch/capture.js
```
