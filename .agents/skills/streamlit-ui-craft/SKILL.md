---
name: streamlit-ui-craft
description: Hướng dẫn tiêu chuẩn xây dựng giao diện Streamlit chuyên nghiệp, bền vững, nhất quán theo mô hình Design Tokens và Component-Driven Development.
---

# Streamlit UI Craft — Tiêu Chuẩn Thiết Kế & Xây Dựng Giao Diện

Kỹ năng này định nghĩa phương pháp xây dựng giao diện Streamlit chất lượng cao (Enterprise SaaS), bảo đảm tính bền bỉ, tính tái sử dụng và khả năng bảo trì lâu dài cho dự án `ba-srs-uml-copilot`.

---

## 1. Cấu Trúc Mã Nguồn Giao Diện (`src/ui/`)

Tất cả mã hiển thị phải được tổ chức tập trung trong thư mục `src/ui/`:

```
src/ui/
├── tokens.py          # NGUỒN SỰ THẬT DUY NHẤT: Bảng màu, typography, spacing, border-radius, shadows
├── styles.py          # MỘT NƠI DUY NHẤT nạp CSS bổ sung, liên kết trực tiếp với tokens.py
├── components.py      # Thư viện hàm giao diện tái sử dụng (MetricCard, Badge, EmptyState, Stepper, ScenarioCard...)
├── components/        # Các thành phần phức tạp / interactive (mermaid_viewer.py)
└── tabs/              # Mô-đun riêng biệt cho từng màn hình / tab nghiệp vụ
    ├── tab_srs.py
    ├── tab_dynamic_models.py
    ├── tab_database.py
    └── tab_export.py
```

---

## 2. Hệ Thống Thước Đo & Quy Tắc Thiết Kế (Design System Rules)

1. **Bảng màu có kỷ luật (Color Palette Discipline)**:
   - **Tối đa 1 màu thương hiệu nhấn (Primary Brand Color)**: Indigo `#4F46E5` (hover `#4338CA`, active `#3730A3`).
   - **Bảng màu trung tính (Neutral Grays)**: Slate/Zinc (`#0F172A`, `#334155`, `#64748B`, `#94A3B8`, `#E2E8F0`, `#F8FAFC`, `#FFFFFF`).
   - **3 màu ngữ nghĩa cố định (Semantic Colors)**:
     - Thành công: `#059669` (Success Green).
     - Cảnh báo: `#D97706` (Warning Amber).
     - Lỗi / Nguy cấp: `#DC2626` (Danger Red).
   - **Tuyệt đối cấm**: Sử dụng màu đỏ cho các nút tác vụ thông thường (nút Submit/Generate phải dùng Primary Indigo).

2. **Quy chuẩn Kiểu chữ (Typography)**:
   - Tối đa **2 font chữ**:
     - Font giao diện chính: `Plus Jakarta Sans` hoặc `Inter` (hỗ trợ 100% dấu tiếng Việt).
     - Font mã nguồn / kỹ thuật: `JetBrains Mono` hoặc `Fira Code`.
   - Thang cỡ chữ cố định:
     - `h1`: 24px / line-height 32px (đậm 700).
     - `h2`: 20px / line-height 28px (đậm 600).
     - `h3` / section title: 16px / line-height 24px (đậm 600).
     - Body: 14px / line-height 20px (thường 400).
     - Caption / helper text: 12px / line-height 16px (thường 400/500).

3. **Thang tỷ lệ khoảng cách (Spacing Scale 4-8-16-24-32)**:
   - `xs`: 4px | `sm`: 8px | `md`: 16px | `lg`: 24px | `xl`: 32px.
   - Không tự ý dùng các khoảng cách tuỳ tiện (`5px`, `11px`, `19px`, `27px`).

4. **Biểu tượng (Iconography)**:
   - Sử dụng **SVG nội tuyến hoặc Material Symbols** đồng bộ thay cho emoji trên các nút bấm, huy hiệu và tiêu đề trang.
   - Emoji chỉ được dùng với mục đích chú thích minh hoạ phi kỹ thuật khi thực sự cần thiết.

---

## 3. Kiến Trúc Cấu Hình Gốc (`.streamlit/config.toml`)

- Mọi thuộc tính giao diện nền tảng (`base`, `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`, `font`) phải được định nghĩa trong `.streamlit/config.toml`.
- File CSS (`styles.py`) **chỉ dùng để bổ sung** các class tuỳ biến (`.metric-card`, `.stepper-item`, `.status-badge`), không ghi đè tràn lan làm gãy cấu trúc responsive của Streamlit.
- **Không dựa vào class CSS sinh tự động của Streamlit (`st-emotion-cache-*`)**. Chỉ sử dụng bộ chọn ngữ nghĩa ổn định (`[data-testid="..."]`) hoặc class do hệ thống tự đặt.

---

## 4. Sử Dụng Thành Phần Chuẩn Của Streamlit Đúng Mục Đích

- **`st.container(border=True)`**: Dùng đóng khung các nhóm thông tin độc lập (Input form, Card danh mục, Metadata preview).
- **`st.columns`**: Dùng phân chia lưới Bento KPI và bố cục hàng ngang.
- **`st.tabs`**: Dùng chuyển đổi ngữ cảnh các tầng đặc tả (SRS ➔ Dynamic Models ➔ Database ➔ Export). Giữ nhãn tab ngắn gọn (< 20 ký tự).
- **`st.expander`**: Dùng cơ chế tiết lộ dần (Progressive Disclosure) cho thông số kỹ thuật (Telemetry, Linter report, SQL schema breakdown).
- **`st.dialog`**: Dùng cho hộp thoại xác nhận tác vụ hoặc bàn làm việc tinh chỉnh chuyên sâu.
- **`st.toast` & `st.status`**: Dùng thông báo phản hồi trạng thái hoạt động tức thì.

---

## 5. Tích Hợp Sơ Đồ Vector (Mermaid / SVG)

- Thành phần `mermaid_viewer.py` phải áp dụng bảng màu và font chữ khớp với `tokens.py`.
- Duy trì nguyên vẹn cơ chế **Lazy Visibility Rendering** (IntersectionObserver) để tránh lỗi crash khi sơ đồ nằm trong tab đang ẩn.
- Cấu hình `useMaxWidth: false` và tính toán tỷ lệ `initialScale >= 0.85` để bảo đảm chữ và liên kết thực thể đọc rõ ràng ngay khi tải trang mà không bắt buộc zoom thủ công.
