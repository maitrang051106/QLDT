# Báo cáo UAT hệ thống QLDT (IT3180 - Nhóm 20)

## 1. Thông tin chung

| Hạng mục | Giá trị |
|---|---|
| Ngày thực hiện | 2026-11-13 |
| Môi trường | Docker Compose đầy đủ (frontend + backend + MySQL + Nginx gateway), chạy tại `http://localhost:8080` |
| Phiên bản dữ liệu | `db/schema.sql` + `db/seed/seed.sql` (17 bảng), migration Alembic `b7e2d41c8a90` |
| Học kỳ kiểm thử | `2026.1` (bắt đầu 2026-09-07, 20 tuần, tuần hiện tại = 10) |
| Phương pháp | UAT API end-to-end bằng script/httpx, kết hợp bộ kiểm thử hồi quy pytest; UAT giao diện bằng trình duyệt thật cho 3 vai trò ADMIN, LECTURER, STUDENT |
| Phạm vi | UC001–UC010: đăng nhập/phân quyền, danh mục môn học, lớp học phần, đăng ký lớp, thời khóa biểu, điểm danh, bảng điểm, học phí và biên lai |

## 2. Môi trường và dữ liệu kiểm thử

- Stack: React 19 + TypeScript + Ant Design 5 (frontend), FastAPI + SQLAlchemy 2 + Alembic (backend), MySQL 8.4, Nginx gateway.
- Cổng: gateway `8080`, MySQL host `3308` (container `3306`).
- Dữ liệu seed: 1019 người dùng, 1000 sinh viên, 18 giảng viên, 100 môn học, 400 lớp học phần, 30 phòng, 1 học kỳ.
- Đơn giá học phí: 450.000 ₫/TCHP (mặc định) và 500.000 ₫/TCHP (CNTT K66).
- Tài khoản kiểm thử:
  - ADMIN: `admin/admin`
  - Giảng viên: `gv001..gv018/123456`
  - Sinh viên: `sv20210001../123456`
- Trạng thái dữ liệu sau UAT (dùng cho đối chiếu):
  - Sinh viên A (`sv20210002`): 4 lớp, 12 TC, hóa đơn 6.075.000 ₫ đã thanh toán, biên lai `BL-2026.1-000001`.
  - Lớp `150001`: 5 sinh viên, đã cấu hình cột điểm 10/30/60, đã điểm danh ngày 2026-11-16, điểm mẫu 8/9/7 → tổng kết 7.5.
  - Lớp `150002`: sĩ số tối đa bị hạ còn 1 để kiểm thử `CLASS_FULL`.
  - Toàn kỳ: 1000 hóa đơn, tổng phải thu 27.675.000 ₫, đã thu 6.075.000 ₫, còn nợ 21.600.000 ₫.

## 3. Kết quả tổng hợp

| Nhóm kiểm thử | Số ca | Đạt | Không đạt |
|---|---:|---:|---:|
| API end-to-end | 96 | 96 | 0 |
| Giao diện (3 vai trò) | 16 | 16 | 0 |
| **Tổng** | **112** | **112** | **0** |

Ghi chú: lần chạy đầu ghi nhận 95/96 do lỗi của script kiểm thử (đánh giá `requests.Response` có HTTP ≥ 400 là falsy). Ca `R09` đã được kiểm tra lại trực tiếp: `POST /api/registrations` cho sinh viên đang 21 TC trả đúng `409 CREDIT_LIMIT_EXCEEDED`. Kết quả cuối cùng là 96/96.

### 3.1 Bộ kiểm thử tự động pytest

Chạy tại thư mục `backend/`:

```bash
pytest -q
```

- Kết quả: **84 test được thu thập, 83 đạt, 1 bỏ qua** (bỏ qua do bộ dữ liệu Feature 10 `TST101` không có trong seed UAT; không phải lỗi).
- Phạm vi pytest: xác thực/RBAC, đăng ký và hủy lớp, giới hạn 12–24 TC, xung đột lịch, đồng thời sĩ số, IDOR, điểm danh/bảng điểm/Excel, học phí một lần, biên lai PDF, cùng các test tích hợp gateway – MySQL – frontend proxy.
- Đã đồng bộ test `test_tuition_permissions_and_payment_limits`: gọi `GET /api/tuition/me` trước khi thanh toán để tạo hóa đơn, đúng luồng giao diện. Không thay đổi mã ứng dụng.

## 4. Kết quả UAT API

### 4.1 Xác thực và phân quyền

| ID | Kịch bản | Kỳ vọng | Thực tế | KQ |
|---|---|---|---|---|
| A01 | Đăng nhập ADMIN | 200, role ADMIN | 200, role=ADMIN | Đạt |
| A02 | Đăng nhập giảng viên `gv001` | 200, role LECTURER | 200, role=LECTURER | Đạt |
| A03 | Đăng nhập sinh viên `sv20210001` | 200, role STUDENT + mã SV | 200, code=20210001 | Đạt |
| A04 | Đăng nhập sai mật khẩu | 401 INVALID_CREDENTIALS | 401 INVALID_CREDENTIALS | Đạt |
| A05 | Đăng nhập thiếu dữ liệu | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| A06 | `/auth/me` với token ADMIN | 200, đúng username | 200, admin | Đạt |
| A07 | `/auth/me` không token | 401 UNAUTHORIZED | 401 UNAUTHORIZED | Đạt |
| A08 | `/auth/me` token không hợp lệ | 401 UNAUTHORIZED | 401 UNAUTHORIZED | Đạt |
| A09 | STUDENT gọi API quản trị học phí | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| A10 | LECTURER tạo môn học | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| A11 | STUDENT gọi lookups lớp | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| A12 | Đăng xuất | 204 | 204 | Đạt |
| A13 | Dùng lại token sau logout (JWT stateless) | Token còn hiệu lực đến khi hết hạn (theo thiết kế) | 200 | Đạt |
| A14 | Không lộ trường nhạy cảm trong `/auth/me` | Không có password_hash/secret | Không có | Đạt |

### 4.2 Danh mục công khai

| ID | Kịch bản | Kỳ vọng | Thực tế | KQ |
|---|---|---|---|---|
| P01 | Xem danh mục môn công khai | 200 + danh sách | 200, 5 mục/trang | Đạt |
| P02 | Tìm môn theo từ khóa | 200 có IT1001 | 200, `['IT1001']` | Đạt |
| P03 | Phân trang `page=0` | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| P04 | Xem lớp học phần khi chưa đăng nhập | 401 UNAUTHORIZED | 401 UNAUTHORIZED | Đạt |

### 4.3 Đăng ký lớp

| ID | Kịch bản | Kỳ vọng | Thực tế | KQ |
|---|---|---|---|---|
| S00 | Đăng nhập 5 sinh viên kiểm thử | 200 | 5/5 thành công | Đạt |
| R01 | Đăng ký lớp 150001 | 201, sĩ số +1 | 201, 0 → 1 | Đạt |
| R02 | Đăng ký trùng lớp | 409 ALREADY_REGISTERED | 409 ALREADY_REGISTERED | Đạt |
| R03 | Đăng ký lớp khác cùng môn | 409 SAME_SUBJECT_REGISTERED | 409 SAME_SUBJECT_REGISTERED | Đạt |
| R04 | Đăng ký lớp trùng lịch | 409 STUDENT_SCHEDULE_CONFLICT | 409 STUDENT_SCHEDULE_CONFLICT | Đạt |
| R05 | Đăng ký đủ 4 lớp / 12 TC | 201 x3, tổng 12 TC | Đúng, 12 TC | Đạt |
| R06 | Hủy khi còn đúng 12 TC (còn 9) | 409 CREDIT_LIMIT_BELOW_MIN | 409 CREDIT_LIMIT_BELOW_MIN | Đạt |
| R07a | Sinh viên B đăng ký 5 lớp / 15 TC | 201 x5, 15 TC | Đúng, 15 TC | Đạt |
| R07b | Hủy khi 15 TC → còn 12 TC | 204, tổng còn 12 | 204, còn 12 TC | Đạt |
| R08 | IDOR: B hủy đăng ký của A | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| R09 | Đang 21 TC, đăng ký thêm 4 TC | 409 CREDIT_LIMIT_EXCEEDED | 409 CREDIT_LIMIT_EXCEEDED (max 24) | Đạt |
| R10a | Admin hạ sĩ số lớp về 1 | 200, maxCapacity=1 | 200, max=1 | Đạt |
| R10b | 2 SV tranh 1 chỗ cuối | 201 và 409 CLASS_FULL | 201, 409 CLASS_FULL | Đạt |
| R11 | Đăng ký lớp không tồn tại | 404 NOT_FOUND | 404 NOT_FOUND | Đạt |
| R12 | ADMIN gọi API đăng ký | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| R13 | Dữ liệu giỏ có tên giảng viên và `registeredByMe` | Có `lecturer.fullName`, `registeredByMe=true` | Đúng | Đạt |

### 4.4 Danh mục môn học và lớp học phần

| ID | Kịch bản | Kỳ vọng | Thực tế | KQ |
|---|---|---|---|---|
| C01 | Lấy lookups môn/GV/phòng/kỳ | 200, đủ 4 danh mục | 200: 100 môn, 18 GV, 30 phòng, 1 kỳ | Đạt |
| C02 | Danh sách lớp học phần phân trang | 200, tổng 400 | 200, total=400 | Đạt |
| C03 | Lọc lớp theo tên giảng viên | 200, mọi kết quả khớp | 200, 20 kết quả khớp | Đạt |
| C04a | Tạo môn học mới | 201 | 201, id=101 | Đạt |
| C04b | Tạo môn trùng mã | 409 DUPLICATE_CODE | 409 DUPLICATE_CODE | Đạt |
| C04c | Xem chi tiết môn vừa tạo | 200 | 200, UATTST | Đạt |
| C04d | Sửa môn học | 200, tên đã sửa | 200 | Đạt |
| C04e | Xóa môn chưa có lớp | 204 | 204 | Đạt |
| C05 | Tạo lớp hợp lệ (Chủ nhật) | 201 | 201, id=401 | Đạt |
| C06 | Tạo lớp trùng mã | 409 DUPLICATE_CODE | 409 DUPLICATE_CODE | Đạt |
| C07 | Trùng phòng/giảng viên cùng giờ | 409 SCHEDULE_CONFLICT | 409 SCHEDULE_CONFLICT | Đạt |
| C08 | Sĩ số vượt sức chứa phòng | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| C09 | Tuần kết thúc vượt số tuần học kỳ | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| C10 | Xóa môn đã có lớp | 409 SUBJECT_HAS_SECTIONS | 409 SUBJECT_HAS_SECTIONS | Đạt |
| C11 | Xóa lớp đã có sinh viên | 409 SECTION_HAS_REGISTRATIONS | 409 SECTION_HAS_REGISTRATIONS | Đạt |
| C12 | Hạ sĩ số dưới số đã đăng ký | 409 CAPACITY_BELOW_ENROLLMENT | 409 CAPACITY_BELOW_ENROLLMENT | Đạt |
| C13 | Kiểm tra xung đột lịch | 200, 2 xung đột ROOM + LECTURER | Đúng | Đạt |
| C14 | Xóa lớp vừa tạo chưa có SV | 204 | 204 | Đạt |

### 4.5 Thời khóa biểu

| ID | Kịch bản | Kỳ vọng | Thực tế | KQ |
|---|---|---|---|---|
| T01 | Học kỳ hiện tại | 200, `2026.1`, tuần 1..20 | 200, tuần 10 | Đạt |
| T02 | TKB sinh viên tuần hiện tại | 200, đủ lớp đã đăng ký | 200, 4 lớp | Đạt |
| T03 | Xem TKB tuần không hợp lệ | 400 INVALID_WEEK | 400 INVALID_WEEK | Đạt |
| T04 | Lịch giảng dạy giảng viên | 200, có tiết dạy | 200, 24 tiết | Đạt |
| T05 | Danh sách lớp giảng viên phụ trách | 200, đúng GV001 | 200, 24 lớp | Đạt |
| T06 | LECTURER gọi TKB sinh viên | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |

### 4.6 Điểm danh và bảng điểm

| ID | Kịch bản | Kỳ vọng | Thực tế | KQ |
|---|---|---|---|---|
| G00 | Đăng ký 2 SV vào lớp 1 | 201, 201 | 201, 201 | Đạt |
| G01 | ADMIN xem danh sách SV lớp 1 | 200, không lộ hash | 200, 5 SV | Đạt |
| G02 | GV001 xem lớp mình | 200 | 200, 5 SV | Đạt |
| G03 | GV002 xem lớp GV001 (IDOR) | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| G04 | Cấu hình cột điểm ban đầu | 200, rỗng | 200, 0 cột | Đạt |
| G05 | LECTURER xem cấu hình cột điểm | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| G06 | Tổng trọng số 50% | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| G07 | Tổng trọng số 100% | 200, 3 cột | 200, 3 cột, tổng 100 | Đạt |
| G08 | Phiếu điểm danh ngày mặc định | 200, có ngày + roster | 200, 20 ngày, 5 SV | Đạt |
| G09 | Điểm danh sai ngày | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| G10 | Lưu điểm danh 2026-11-16 | 200, tất cả PRESENT | 200, PRESENT | Đạt |
| G11 | Nhập điểm thiếu cột | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| G12 | Tính điểm tổng kết, làm tròn 0.5 | 200, tổng kết 7.5 | 200, 7.5 | Đạt |
| G13 | Đổi cấu hình sau khi đã nhập điểm | 409 GRADE_COMPONENTS_LOCKED | 409 GRADE_COMPONENTS_LOCKED | Đạt |
| G14 | Xuất Excel điểm danh | Tệp `.xlsx` | 200, `application/...sheet`, magic `PK` | Đạt |
| G15 | Xuất Excel bảng điểm | Tệp `.xlsx` | 200, `application/...sheet`, magic `PK` | Đạt |
| G16 | GV002 xuất Excel lớp GV001 | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| G17 | ADMIN lưu điểm danh | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| G18 | STUDENT xem danh sách lớp | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |

### 4.7 Học phí và biên lai

| ID | Kịch bản | Kỳ vọng | Thực tế | KQ |
|---|---|---|---|---|
| U01 | Danh sách đơn giá | 200, có 2 đơn giá | 200, 2 đơn giá | Đạt |
| U02 | Tạo đơn giá 0 đồng | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| U03 | Ngày kết thúc trước ngày bắt đầu | 400 VALIDATION_ERROR | 400 VALIDATION_ERROR | Đạt |
| U04 | Phát hành hóa đơn cho SV A | 200, tạo ≥1 | 200, tạo 1, bỏ qua 0 | Đạt |
| U05 | SV xem hóa đơn | 200, `amountDue` = tổng items | 6.075.000 = 6.075.000 (4 mục) | Đạt |
| U06 | Admin tra cứu theo MSSV | 200, thấy SV | 200, 1 kết quả | Đạt |
| U07 | Báo cáo tổng hợp thu | 200, số liệu khớp | 2 hóa đơn, phải thu 6.075.000, đã thu 0, nợ 6.075.000 | Đạt |
| U08 | Thanh toán một lần toàn bộ | 201, sinh biên lai | 201, `BL-2026.1-000001`, 6.075.000 | Đạt |
| U08b | Trạng thái sau thanh toán | PAID, nợ 0 | PAID, nợ 0 | Đạt |
| U09 | Lặp cùng `idempotencyKey` | Trả cùng biên lai, không thu thêm | Cùng id, cùng số tiền | Đạt |
| U10 | Thanh toán lại với key mới khi đã PAID | 409 INVOICE_ALREADY_PAID | 409 INVOICE_ALREADY_PAID | Đạt |
| U11 | Danh sách biên lai | 200, 1 biên lai | 200, 1 | Đạt |
| U12 | Chi tiết biên lai | 200, đúng số | 200, `BL-2026.1-000001` | Đạt |
| U13 | Tải PDF biên lai | 200, `application/pdf`, `%PDF` | Đúng | Đạt |
| U14 | SV khác xem biên lai của A | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |
| U15 | ADMIN xem biên lai | 200 | 200 | Đạt |
| U16 | PDF biên lai không tồn tại | 404 NOT_FOUND | 404 NOT_FOUND | Đạt |
| U17 | Tính/cập nhật hóa đơn toàn kỳ | 200, bỏ qua hóa đơn đã nộp | 200, tạo 999, bỏ qua 1 | Đạt |
| U18 | LECTURER gọi thanh toán | 403 FORBIDDEN | 403 FORBIDDEN | Đạt |

## 5. Kết quả UAT giao diện

| ID | Vai trò | Kịch bản | Kết quả |
|---|---|---|---|
| UI-01 | Công khai | Mở `/courses`, xem 100 học phần, tìm `IT1003`, mở modal chi tiết | Đạt |
| UI-02 | Công khai | Đăng nhập sai mật khẩu, hiển thị thông báo lỗi rõ ràng | Đạt |
| UI-03 | Sinh viên | `/app/sections`: 400 lớp/40 trang, hiển thị giảng viên, trạng thái đã đăng ký/đã đầy, giỏ lớp, TKB dự kiến, cảnh báo trùng lịch và dưới 12 TC | Đạt |
| UI-04 | Sinh viên | `/app/registrations`: 4 lớp, 12 TC, tiến độ tín chỉ, tên giảng viên, nút hủy | Đạt |
| UI-05 | Sinh viên | `/app/timetable`: tuần 10, ngày 2026-11-09, 4 lớp kèm giảng viên | Đạt |
| UI-06 | Sinh viên | `/app/tuition`: tổng 6.075.000 ₫, đã nộp đủ, 4 mục chi tiết, tab biên lai, modal biên lai, nút tải PDF | Đạt |
| UI-07 | Sinh viên | Truy cập trực tiếp `/app/subjects` bị chặn với màn hình 403 | Đạt |
| UI-08 | Giảng viên | `/app/timetable`: 24 tiết dạy trong tuần | Đạt |
| UI-09 | Giảng viên | `/app/sections`: 24 lớp phụ trách | Đạt |
| UI-10 | Giảng viên | Mở lớp 150001: danh sách 5 SV, sĩ số 5/40 | Đạt |
| UI-11 | Giảng viên | Tab Điểm danh: ngày 2026-11-16, 5 SV “Có mặt”, có nút lưu và xuất Excel | Đạt |
| UI-12 | Giảng viên | Tab Bảng điểm: trọng số 10/30/60, điểm 8/9/7 → tổng kết 7.5, có nút lưu và xuất Excel | Đạt |
| UI-13 | Admin | `/app/subjects`: 100 môn, nút xóa bị vô hiệu hóa với môn đã có lớp | Đạt |
| UI-14 | Admin | `/app/sections`: 400 lớp, sĩ số, giảng viên, phòng, thao tác danh sách SV/sửa/cấu hình điểm/xóa | Đạt |
| UI-15 | Admin | `/app/timetable/manage`: 400 lớp, chọn 150001, form phân công điền sẵn | Đạt |
| UI-16 | Admin | `/app/tuition/manage`: 1000 hóa đơn, tổng phải thu/đã thu/còn nợ; tab đơn giá có 2 mức giá | Đạt |

## 6. Kết luận

- Toàn bộ 112 ca UAT trọng yếu đều đạt trên môi trường Docker đầy đủ.
- Các quy tắc nghiệp vụ chính được xác nhận: giới hạn 12–24 TC, chống trùng lớp/trùng môn/trùng lịch, sức chứa lớp, phân quyền theo vai trò, chống IDOR, điểm tổng kết làm tròn 0.5, khóa cấu hình điểm sau khi nhập, học phí thanh toán một lần và biên lai PDF.
- Không phát hiện lỗi chức năng cần ghi nhận trong phạm vi UAT. Các quan sát không phải lỗi được tổng hợp tại [bug-log.md](bug-log.md).
