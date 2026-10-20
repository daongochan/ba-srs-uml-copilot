"""Sample customer meeting notes for instant testing and demonstration."""

from typing import Dict, Any

SAMPLE_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "cinema_booking": {
        "title": "Hệ thống đặt vé và quản lý suất chiếu rạp chiếu phim",
        "domain": "Giải trí & Rạp chiếu phim (Cinema Management)",
        "summary": "Quản lý phòng chiếu, sơ đồ ghế, cơ chế giữ chỗ tạm thời 10 phút, đặt vé đa kênh và thanh toán hóa đơn.",
        "meeting_notes": """# BIÊN BẢN GHI CHÚ HỌP KHÁCH HÀNG (MEETING NOTES)
**Dự án:** Hệ thống Quản trị Suất chiếu & Đặt vé Rạp chiếu phim (CineMax System)
**Khách hàng:** Chuỗi cụm rạp CineMax Vietnam
**Đại diện tham dự:**
- Khách hàng: Ông Nguyễn Văn Nam (Giám đốc Vận hành), Bà Lê Thanh Hà (Trưởng phòng Vé & Dịch vụ)
- BA Team: Lead Business Analyst & Solution Architect

## 1. Bối cảnh & Mục tiêu Kinh doanh
- Hiện tại chuỗi có 8 cụm rạp tại Hà Nội và TP.HCM, bán vé chủ yếu tại quầy POS và qua đối tác trung gian với chi phí hoa hồng cao (12%).
- Mục tiêu: Xây dựng nền tảng đặt vé trực tuyến đa kênh (Web, Mobile App) tích hợp bán vé tại quầy POS, tối ưu tỷ lệ lấp đầy phòng chiếu (mục tiêu tăng 30% doanh thu online), loại bỏ triệt để hiện tượng trùng ghế (double booking).

## 2. Các Yêu cầu Nghiệp vụ Chi tiết

### A. Quản lý Rạp, Phòng chiếu & Suất chiếu
- Mỗi cụm rạp có nhiều phòng chiếu (Phòng Standard, 3D, IMAX, VIP).
- Mỗi phòng chiếu được thiết lập sơ đồ ghế ma trận (Hàng A-K, Cột 1-16), phân loại ghế: Ghế thường (Standard), Ghế VIP, Ghế đôi (Sweetbox).
- Nhân viên quản lý lịch chiếu tạo suất chiếu theo ngày/giờ, gán phim, gán phòng chiếu.
- Bảng giá vé động: Giá cơ bản theo loại ghế, phụ thu suất chiếu cuối tuần (Thứ 6, Thứ 7, Chủ Nhật) và suất chiếu đặc biệt (Sneak Show).

### B. Quy trình Đặt vé & Giữ chỗ tạm thời (Seat Locking)
- Khách hàng xem danh sách phim đang chiếu, sắp chiếu, chọn rạp, ngày xem và suất chiếu.
- Khách hàng xem sơ đồ ghế thời gian thực (trạng thái: Ghế trống, Ghế đang được giữ chỗ, Ghế đã bán).
- Khi khách hàng nhấn chọn từ 1 đến tối đa 8 ghế:
  + Hệ thống kích hoạt cơ chế khóa ghế tạm thời (Seat Lock) trong vòng 10 phút. Trong thời gian này, khách hàng khác không thể chọn các ghế này.
  + Đồng hồ đếm ngược hiển thị trên màn hình của khách hàng.
  + Nếu hết 10 phút mà khách hàng chưa hoàn tất thanh toán, hệ thống tự động giải phóng ghế (Release Lock) về trạng thái còn trống và hủy phiên giao dịch.

### C. Mua kèm Combo Bắp Nước & Áp dụng Khuyến mại
- Trước bước thanh toán, khách hàng có thể chọn thêm các combo bắp nước (Single Combo, Couple Combo).
- Khách hàng có thể nhập mã giảm giá (Voucher/Promo Code) hoặc dùng điểm tích lũy thành viên CineMax Member.

### D. Thanh toán & Xuất vé điện tử
- Tích hợp cổng thanh toán trực tuyến: Thẻ tín dụng/ghi nợ quốc tế, ATM nội địa, Cổng VNPay QR, Ví điện tử MoMo/ZaloPay.
- Sau khi cổng thanh toán phản hồi giao dịch thành công (IPN callback):
  + Cập nhật trạng thái ghế sang "Đã bán" (Sold).
  + Tạo bản ghi Đơn hàng (Order) và Vé (Ticket) với mã đặt chỗ duy nhất (Booking Code).
  + Tự động sinh mã QR Code động cho từng vé và gửi email xác nhận kèm vé điện tử (e-Ticket PDF).
- Tại rạp, nhân viên soát vé dùng máy quét cầm tay hoặc camera điện thoại quét mã QR của khách để check-in vào phòng chiếu.

## 3. Yêu cầu Phi chức năng & Kỹ thuật
- **Độ tin cậy & Tính nhất quán (ACID):** Đảm bảo cơ chế Seat Lock an toàn tuyệt đối khi có hàng ngàn người cùng đặt vé một suất chiếu hot (Block Double Booking bằng Distributed Lock / Database Row-level lock).
- **Hiệu năng & Khả năng chịu tải:** Đáp ứng ít nhất 3.000 lượt đặt vé đồng thời vào khung giờ mở bán phim bom tấn; thời gian phản hồi API tra cứu trạng thái ghế < 250ms.
- **Bảo mật:** Dữ liệu thanh toán không lưu trữ thông tin thẻ trực tiếp (tuân thủ PCI-DSS), mã QR vé được mã hóa kèm chữ ký số chống làm giả vé.
""",
    },
    "bus_logistics": {
        "title": "Hệ thống quản lý điều hành xe khách liên tỉnh",
        "domain": "Vận tải hành khách & Logistics (Intercity Bus & Logistics)",
        "summary": "Điều hành đội xe 150 phương tiện, quản lý tuyến đường, lịch chạy xe, đặt vé chọn giường và ký gửi hàng hóa liên tỉnh.",
        "meeting_notes": """# BIÊN BẢN GHI CHÚ HỌP KHÁCH HÀNG (MEETING NOTES)
**Dự án:** Hệ thống Quản trị & Điều hành Xe khách Liên tỉnh (Bus & Parcel Logistics Hub)
**Khách hàng:** Công ty Cổ phần Vận tải Hành khách Phương Nam Express
**Đại diện tham dự:**
- Khách hàng: Ông Trần Đình Trọng (Tổng Giám đốc), Ông Vũ Hữu Tài (Trưởng ban Điều hành Đội xe)
- BA Team: Lead Business Analyst & Domain Consultant

## 1. Bối cảnh & Mục tiêu Kinh doanh
- Phương Nam Express sở hữu hơn 150 xe giường nằm 34 phòng và Limousine 22 phòng, phục vụ 18 tuyến đường xuyên tỉnh khu vực Miền Trung - Tây Nguyên - Nam Bộ.
- Tình trạng hiện tại: Bán vé và quản lý gửi hàng dùng sổ sách kết hợp phần mềm cũ cục bộ, thường xuyên thất lạc hàng hóa ký gửi và trùng giường nằm vào mùa lễ tết.
- Mục tiêu: Xây dựng nền tảng phần mềm tập trung quản lý toàn diện từ lịch tài, bán vé theo số giường đến giao nhận hàng ký gửi bằng mã vạch vận đơn (Waybill Tracking).

## 2. Các Yêu cầu Nghiệp vụ Chi tiết

### A. Quản lý Tuyến đường, Trạm dừng & Giá cước
- Danh mục tuyến đường liên tỉnh (ví dụ: Tuyến Sài Gòn - Đà Lạt, Tuyến Sài Gòn - Buôn Ma Thuột, Tuyến Đà Nẵng - Quy Nhơn).
- Mỗi tuyến có danh sách các trạm dừng đón/trả khách cố định kèm thứ tự và thời gian dự kiến đến.
- Bảng giá vé hành khách quy định theo chặng (đón chặng nào tính tiền chặng đó) và theo loại xe (Giường nằm thường, Giường VIP Cabin).

### B. Quản lý Đội xe, Phân công Tài xế & Lịch chạy
- Quản lý thông tin phương tiện: Biển số xe, số khung, số máy, ngày hết hạn kiểm định, hạn bảo dưỡng, sơ đồ số giường (Tầng 1 - Tầng 2).
- Quản lý nhân sự đội xe: Tài xế chính, tài xế phụ, phụ xe. Ràng buộc an toàn: Không phân tài xế lái liên tục quá 4 giờ hoặc quá 10 giờ trong ngày.
- Điều phối viên tạo Chuyến xe (Trip): Gán xe, gán tài xế, ngày khởi hành, giờ xuất bến, trạng thái chuyến (Chờ khởi hành, Đang di chuyển, Đã đến bến, Hoãn/Hủy).

### C. Đặt vé Hành khách & Sơ đồ Giường nằm
- Khách hàng hoặc nhân viên tổng đài chọn Tuyến, Ngày đi, Giờ chạy.
- Hiển thị trực quan sơ đồ giường nằm 2 tầng; khách hàng chọn đích danh vị trí giường mong muốn (ví dụ: Tầng 1 dãy A giường 02).
- Hỗ trợ 2 hình thức thanh toán: Thanh toán online (chuyển khoản/cổng thanh toán) giữ chỗ ngay hoặc Đặt giữ chỗ thanh toán tại quầy trước giờ xuất bến 60 phút.
- Gửi SMS Brandname và tin nhắn Zalo ZNS chứa mã vé, biển số xe, số điện thoại tài xế và vị trí đón khách.

### D. Nghiệp vụ Ký gửi Hàng hóa Liên tỉnh (Parcel Delivery)
- Khách hàng mang kiện hàng đến văn phòng nhà xe để gửi đi:
  + Nhân viên nhận hàng kiểm tra, cân trọng lượng (kg) hoặc đo kích thước thể tích (Dài x Rộng x Cao).
  + Nhập thông tin người gửi, số điện thoại, thông tin người nhận, trạm nhận hàng.
  + Tính cước phí tự động dựa trên khoảng cách chặng, cân nặng và loại hàng (hàng tiêu dùng, điện tử, đông lạnh).
  + Tùy chọn thu hộ tiền hàng (Ship COD) nếu có.
- Hệ thống in Mã vận đơn dạng Barcode/QR code (Waybill) gồm 3 liên: Dán vào kiện hàng, giao người gửi làm biên lai, lưu hồ sơ chuyến xe.
- Phụ xe dùng điện thoại quét mã vận đơn để xác nhận "Hàng đã xếp lên xe [Biển số]".
- Khi xe đến trạm đích, kho đích quét nhận kiện hàng và hệ thống tự động gửi SMS thông báo kèm mã OTP nhận hàng đến điện thoại người nhận.
- Khi người nhận đến lấy hàng, xuất trình OTP và thanh toán cước (nếu người nhận trả cước).

## 3. Yêu cầu Phi chức năng & Kỹ thuật
- **Khả năng Offline-First trên App Tài xế:** Ứng dụng di động của tài xế và phụ xe có khả năng hoạt động ngay cả khi xe đi qua đoạn đèo dốc mất sóng di động, đồng bộ dữ liệu ngay khi có mạng trở lại.
- **Truy vết đơn hàng (Traceability):** Khách hàng có thể tra cứu lịch sử hành trình kiện hàng trên website thời gian thực theo mã vận đơn.
- **Tính toàn vẹn & Phân quyền:** Phân quyền chặt chẽ giữa Điều phối tổng, Trưởng bến, Thu ngân phòng vé, Nhân viên kho hàng và Tài xế.
""",
    },
    "warehouse_inventory": {
        "title": "Hệ thống quản lý xuất nhập tồn kho hàng",
        "domain": "Quản trị Kho & Chuỗi cung ứng (WMS - Warehouse Management)",
        "summary": "Quản lý 3 kho trung tâm & 12 kho vệ tinh, quy trình nhập kho theo PO, xuất kho FIFO theo Pick List, kiểm kê định kỳ và cảnh báo tồn an toàn.",
        "meeting_notes": """# BIÊN BẢN GHI CHÚ HỌP KHÁCH HÀNG (MEETING NOTES)
**Dự án:** Hệ thống Quản trị Xuất Nhập Tồn & Kho Thông minh (Smart WMS Pro)
**Khách hàng:** Công ty Cổ phần Phân phối Công nghệ LogiTech Pro
**Đại diện tham dự:**
- Khách hàng: Ông Đỗ Quốc Bảo (Giám đốc Chuỗi cung ứng), Bà Hoàng Mai Lan (Trưởng phòng Quản lý Kho)
- BA Team: Lead Business Analyst & Enterprise Architect

## 1. Bối cảnh & Mục tiêu Kinh doanh
- LogiTech Pro phân phối thiết bị gia dụng thông minh và linh kiện phụ tùng cho hơn 400 đại lý toàn quốc với 3 kho trung tâm (Hà Nội, Đà Nẵng, Bình Dương) và 12 kho chi nhánh vệ tinh.
- Vấn đề nhức nhối: Số liệu tồn kho thực tế lệch so với sổ sách kế toán tới 4.2%; thời gian nhặt hàng đóng gói chậm do không biết hàng nằm ở vị trí nào; nhiều mặt hàng hết hạn hoặc tồn kho quá đát (Dead Stock) gây tồn đọng vốn hơn 15 tỷ đồng.
- Mục tiêu: Chuẩn hóa 100% quy trình kho theo chuẩn FIFO (First-In, First-Out), định danh vị trí kho theo cấu trúc Kệ - Tầng - Ô (Bin-Location), giảm tỷ lệ sai sót tồn kho xuống dưới 0.1%.

## 2. Các Yêu cầu Nghiệp vụ Chi tiết

### A. Quản lý Danh mục Hàng hóa, Vị trí Lưu kho & Đơn vị tính
- Quản lý sản phẩm: Mã SKU, Mã vạch Barcode/EAN-13, Tên hàng, Nhóm ngành, Đơn vị tính cơ sở (Cái, Chiếc) và Đơn vị tính quy đổi (Thùng, Kiện, Pallet).
- Quản lý hạn sử dụng (Expiry Date) và số Lô sản xuất (Lot/Batch Number) cho các nhóm linh kiện đặc thù.
- Sơ đồ hóa kho hàng theo mô hình 3 cấp độ: Khu vực (Zone) -> Dãy/Kệ (Rack) -> Tầng (Shelf) -> Ô lưu trữ (Bin Location). Mỗi ô đều có mã vạch định danh.

### B. Quy trình Nhập kho (Goods Receipt - GR)
- Nhập kho mua hàng từ Nhà cung cấp dựa trên Đơn đặt hàng mua (Purchase Order - PO) đã được phê duyệt.
- Thủ kho quét mã vạch kiểm tra số lượng thực nhận, phân loại hàng đạt chuẩn (QC Passed) và hàng lỗi trả về (QC Rejected).
- Hệ thống tự động đề xuất vị trí lưu kho tối ưu (Put-away Strategy) dựa trên kích thước, trọng lượng và tần suất luân chuyển của sản phẩm (hàng bán nhanh để gần cửa xuất).
- In và dán nhãn Lot/Bin lên từng pallet/thùng trước khi xếp vào kệ. Sinh Phiếu nhập kho chính thức cập nhật tức thời số lượng tồn.

### C. Quy trình Xuất kho (Goods Issue - GI) & Soạn hàng (Order Picking)
- Tiếp nhận Đơn hàng xuất bán (Sales Order) hoặc Yêu cầu điều chuyển kho nội bộ (Transfer Request).
- Hệ thống áp dụng nghiêm ngặt nguyên tắc FIFO: Tự động chỉ định xuất các lô hàng nhập trước hoặc các lô có hạn dùng gần nhất (FEFO).
- Sinh Danh sách soạn hàng (Pick List) thông minh: Gom đơn và sắp xếp lộ trình di chuyển của nhân viên kho theo thứ tự các ô kệ ngắn nhất, tránh đi lòng vòng.
- Nhân viên kho dùng máy quét PDA quét mã Barcode ô kệ và mã hàng để xác nhận việc nhặt hàng chính xác.
- Đóng gói, dán nhãn kiện hàng vận chuyển và in Phiếu xuất kho kiêm Biên bản bàn giao vận chuyển.

### D. Quy trình Kiểm kê Định kỳ & Cân đối Kho (Stocktake & Cycle Count)
- Cho phép tạo đợt kiểm kê toàn bộ kho hoặc kiểm kê cuốn chiếu theo từng nhóm SKU/Khu vực kệ mà không cần dừng hoạt động cả kho.
- Nhân viên quét kiểm đếm thực tế; hệ thống tự động so khớp với số liệu tồn trên hệ thống và lập Bảng chênh lệch thừa/thiếu.
- Thiết lập quy trình duyệt Phiếu điều chỉnh tồn kho (Stock Adjustment) với đầy đủ lý do (hư hỏng, rơi vỡ, thất thoát) và cấp phê duyệt theo phân quyền hạn mức giá trị.

### E. Cảnh báo Tồn kho An toàn & Đề xuất Đặt hàng
- Thiết lập định mức Tồn tối thiểu (Safety Stock / Min) và Tồn tối đa (Max Stock) cho từng SKU tại từng kho cụ thể.
- Khi Tồn kho khả dụng (Available = On-hand - Reserved) chạm ngưỡng tối thiểu, hệ thống tự động kích hoạt cảnh báo cảnh báo màu đỏ trên Dashboard và gửi email đến Trưởng phòng Thu mua.
- Tự động gợi ý số lượng cần mua thêm (Reorder Quantity) dựa trên tốc độ bán trung bình 30 ngày qua (Lead Time Demand).

## 3. Yêu cầu Phi chức năng & Kỹ thuật
- **Tính toán Tồn kho Tức thời (Real-time Inventory Balance):** Mọi thao tác xuất/nhập/chuyển kho phải phản ánh vào số dư tồn kho khả dụng ngay lập tức mà không có độ trễ batch-job.
- **Nhật ký Truy vết Toàn diện (Audit Trail):** Mọi giao dịch thay đổi số lượng tồn đều lưu vết định danh: Ai làm, Vào thời điểm nào, Từ số lượng bao nhiêu thành bao nhiêu, Dựa trên chứng từ nào.
- **Tích hợp:** Khả năng mở API RESTful chuẩn để kết nối đồng bộ 2 chiều với phần mềm Kế toán (MISA/FAST) và hệ thống ERP (SAP/Odoo).
""",
    },
}


def get_scenario_keys() -> list[str]:
    """Trả về danh sách các key của kịch bản mẫu."""
    return list(SAMPLE_SCENARIOS.keys())


def get_scenario_by_key(key: str) -> Dict[str, Any]:
    """Lấy thông tin chi tiết của một kịch bản theo key."""
    if key not in SAMPLE_SCENARIOS:
        raise KeyError(f"Kịch bản '{key}' không tồn tại trong danh mục mẫu.")
    return SAMPLE_SCENARIOS[key]
