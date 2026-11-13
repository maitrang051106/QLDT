# Hướng dẫn sử dụng hệ thống QLDT (IT3180 - Nhóm 20)

## 1. Giới thiệu

Hệ thống Quản lý Đào tạo (QLDT) hỗ trợ ba nhóm người dùng:

- **Sinh viên**: tra cứu học phần, đăng ký lớp, xem thời khóa biểu, xem học phí và biên lai.
- **Giảng viên**: xem lịch giảng dạy, lớp phụ trách, điểm danh, nhập điểm và xuất Excel.
- **Quản trị viên**: quản lý môn học, lớp học phần, lịch phân công, cấu hình điểm và học phí.

Hệ thống chỉ có **một học kỳ hiện tại là 2026.1** (Học kỳ 1 năm học 2026-2027). Các màn hình nghiệp vụ tự động gắn với học kỳ này, không có ô chọn đổi học kỳ.

## 2. Truy cập và đăng nhập

### 2.1 Địa chỉ

- Giao diện chính: `http://localhost:8080`
- Tra cứu học phần công khai (không cần đăng nhập): `http://localhost:8080/courses`
- Tài liệu API (Swagger): `http://localhost:8080/api/docs`

### 2.2 Tài khoản

| Vai trò | Tên đăng nhập | Mật khẩu |
|---|---|---|
| Quản trị viên | `admin` | `admin` |
| Giảng viên | `gv001` … `gv018` | `123456` |
| Sinh viên | `sv20210001` … `sv20211000` | `123456` |

Tài khoản do nhà trường cấp; hệ thống không hỗ trợ đăng ký mới.

### 2.3 Đăng nhập, đăng xuất

1. Mở `http://localhost:8080/login`.
2. Nhập tên đăng nhập và mật khẩu, bấm **Đăng nhập**.
3. Hệ thống tự chuyển đến trang phù hợp với vai trò:
   - Sinh viên → **Đăng ký lớp**
   - Giảng viên → **Lịch giảng dạy**
   - Quản trị viên → **Môn học**
4. Bấm **Đăng xuất** ở cuối thanh điều hướng bên trái để kết thúc phiên.

Nếu nhập sai, hệ thống hiển thị: “Tên đăng nhập hoặc mật khẩu chưa chính xác.” Phiên đăng nhập hết hạn sẽ tự chuyển về trang đăng nhập.

## 3. Hướng dẫn cho Sinh viên

### 3.1 Tra cứu học phần công khai

- Mở `/courses` để xem danh mục học phần, không cần đăng nhập.
- Gõ mã hoặc tên học phần vào ô **Tìm học phần** để lọc.
- Bấm vào một dòng để xem chi tiết: mã, tên, số tín chỉ, mô tả.
- Bấm **Xóa lọc** để trở về danh sách đầy đủ.

### 3.2 Đăng ký lớp

Vào menu **Đăng ký lớp** (`/app/sections`).

**Bộ lọc và tìm kiếm:**

- Ô tìm kiếm: mã lớp, mã học phần hoặc tên học phần.
- Ô **Trường / Viện / Khoa**: lọc theo đơn vị.
- Ô **Giảng viên**: lọc theo tên hoặc mã giảng viên.
- Chọn **Thứ trong tuần** và **Kíp học** (sáng/chiều) nếu cần.
- Tick **Ẩn lớp trùng lịch hiện tại** để loại các lớp trùng với lớp đã đăng ký.
- Tick **Chỉ hiện lớp còn chỗ** để loại lớp đã đầy.

**Đăng ký:**

1. Bấm **Thêm vào giỏ** ở lớp muốn học. Lớp đã có trong giỏ sẽ hiện **Đã trong giỏ**; lớp đã đăng ký sẽ hiện **Đã đăng ký**.
2. Kiểm tra cột **Giảng viên**, **Lịch học**, **Tuần học**, **Phòng** trước khi gửi.
3. Xem khung **Giỏ lớp đăng ký** bên phải:
   - Số lớp và tổng tín chỉ (giới hạn **12–24 tín chỉ**).
   - Cảnh báo nếu giỏ có lớp trùng lịch hoặc dưới mức tối thiểu.
   - Khung **Thời khóa biểu dự kiến** hiển thị các lớp đã đăng ký và lớp đang chọn; lớp trùng lịch được đánh dấu.
4. Bấm **Gửi toàn bộ đăng ký**. Hệ thống kiểm tra lại toàn bộ và trả kết quả:
   - Đăng ký thành công: lớp chuyển sang trạng thái **Đã đăng ký**.
   - Nếu có lỗi, hệ thống thông báo rõ nguyên nhân (xem mục 6).

**Lưu ý:**

- Không đăng ký trùng một lớp, không đăng ký hai lớp của cùng một môn.
- Không đăng ký lớp trùng thời gian với lớp đã có.
- Không vượt quá 24 tín chỉ; không để tổng tín chỉ dưới 12 khi hủy lớp.

### 3.3 Xem lớp đã đăng ký

Vào menu **Lớp đã đăng ký** (`/app/registrations`).

- Xem tổng số tín chỉ, tổng số lớp và tiến độ tín chỉ trong học kỳ.
- Mỗi lớp hiển thị mã lớp, tên môn, số tín chỉ, thứ/tiết, tuần học và giảng viên.
- Bấm **Hủy đăng ký** để hủy một lớp. Nếu hủy làm tổng tín chỉ xuống dưới 12, hệ thống sẽ từ chối và báo lỗi.

### 3.4 Xem thời khóa biểu

Vào menu **Thời khóa biểu** (`/app/timetable`).

- Hệ thống mở tuần hiện tại (tuần 10 của học kỳ 2026.1).
- Dùng nút **‹**, **›** hoặc ô số tuần để xem tuần trước/sau; bấm **Tuần hiện tại** để quay lại.
- Mỗi ô hiển thị mã lớp, tên môn, tiết, phòng và giảng viên.
- Chú giải màu: lớp đã đăng ký, lớp đang chọn, lớp có xung đột.

### 3.5 Học phí và biên lai

Vào menu **Học phí & biên lai** (`/app/tuition`).

- Xem **Tổng học phí**, **Phải nộp**, **Đã nộp**, **Còn nợ**.
- Tab **Chi tiết môn học**: mã môn, tên môn, số tín chỉ, TCHP, đơn giá/TCHP và thành tiền.
- Nếu hóa đơn chưa được phát hành, số liệu có thể bằng 0. Khi đó cần quản trị viên phát hành hóa đơn cho học kỳ.
- Khi có hóa đơn chưa thanh toán, bấm **Nộp học phí**. Hệ thống thanh toán **một lần cho toàn bộ số còn nợ** (không chia đợt), sau đó cấp biên lai.
- Sau khi thanh toán:
  - Trạng thái chuyển thành **Đã hoàn tất**, nút **Nộp học phí** bị vô hiệu hóa, **Còn nợ** bằng 0.
  - Tab **Hóa đơn đã nộp** hiển thị số biên lai, số tiền, số tiền bằng chữ, thời điểm cấp.
  - Bấm **Xem** để xem chi tiết biên lai; bấm **Tải PDF** để tải biên lai điện tử.

## 4. Hướng dẫn cho Giảng viên

### 4.1 Lịch giảng dạy

Vào menu **Lịch giảng dạy** (`/app/timetable`).

- Xem các tiết dạy theo tuần, gồm mã lớp, tên môn, tiết và phòng.
- Dùng nút chuyển tuần giống màn hình thời khóa biểu của sinh viên.
- Không xem được thời khóa biểu của sinh viên (chỉ sinh viên và quản trị viên có quyền phù hợp).

### 4.2 Lớp phụ trách và danh sách sinh viên

Vào menu **Lớp phụ trách** (`/app/sections`).

- Mỗi thẻ hiển thị mã lớp, học kỳ, tên môn và mã môn.
- Bấm **Danh sách, điểm danh & điểm** để mở lớp.
- Tab **Danh sách sinh viên**: xem STT, MSSV, họ tên, email, khóa, ngành, thời điểm đăng ký và sĩ số hiện tại/sức chứa.

### 4.3 Điểm danh

Trong lớp phụ trách, chọn tab **Điểm danh**.

1. Chọn **Ngày điểm danh** trong danh sách các ngày có tiết học của lớp.
2. Với từng sinh viên, chọn trạng thái: **Có mặt**, **Vắng**, **Muộn**, **Có phép**.
3. Bấm **Lưu điểm danh** để ghi nhận.
4. Bấm **Xuất Excel điểm danh** để tải phiếu điểm danh của ngày đang chọn.

Lưu ý: chỉ chọn được ngày thuộc lịch học của lớp; ngày khác sẽ bị từ chối.

### 4.4 Nhập điểm và xuất bảng điểm

Trong lớp phụ trách, chọn tab **Bảng điểm**.

- Phần đầu hiển thị cấu hình cột điểm do quản trị viên thiết lập, ví dụ: Chuyên cần 10%, Giữa kỳ 30%, Cuối kỳ 60%.
- Nhập điểm từng cột cho từng sinh viên (thang điểm 0–10).
- **Điểm tổng kết** được tính tự động theo trọng số và làm tròn về 0,5 gần nhất.
- Bấm **Lưu bảng điểm** để ghi nhận.
- Bấm **Xuất Excel bảng điểm** để tải bảng điểm của lớp.

Lưu ý:

- Phải nhập đủ các cột điểm bắt buộc; thiếu cột sẽ bị từ chối.
- Sau khi đã nhập điểm, quản trị viên không thể thay đổi cấu hình cột điểm của lớp (khóa cấu hình).

## 5. Hướng dẫn cho Quản trị viên

### 5.1 Quản lý môn học

Vào menu **Môn học** (`/app/subjects`).

- Xem danh sách môn: mã môn, tên môn, số tín chỉ, số lớp đã mở.
- Bấm **Thêm môn học** để tạo môn mới: nhập mã, tên, số tín chỉ, mô tả.
- Bấm **Sửa** để cập nhật thông tin môn.
- Bấm **Xóa** để xóa môn chưa có lớp. Môn đã có lớp sẽ bị khóa xóa.
- Mã môn phải là duy nhất; trùng mã sẽ bị từ chối.

### 5.2 Quản lý lớp học phần

Vào menu **Lớp học phần** (`/app/sections`).

- Xem danh sách lớp: mã lớp, môn học, giảng viên, phòng, lịch, sĩ số.
- Bấm **Mở lớp học phần** để tạo lớp mới. Chọn môn, học kỳ (cố định 2026.1), giảng viên, phòng, thứ, tiết bắt đầu/kết thúc, tuần bắt đầu/kết thúc, sĩ số tối đa.
- Bấm **Sửa** để điều chỉnh lớp.
- Bấm **Cấu hình điểm** để thiết lập các cột điểm và trọng số cho lớp.
- Bấm **Danh sách SV** để xem danh sách sinh viên đã đăng ký.
- Bấm **Xóa** để xóa lớp chưa có sinh viên.

Ràng buộc quan trọng:

- Mã lớp duy nhất.
- Phòng và giảng viên không được trùng lịch với lớp khác.
- Sĩ số tối đa không vượt sức chứa phòng.
- Tuần kết thúc không vượt quá số tuần của học kỳ.
- Không hạ sĩ số tối đa xuống dưới số sinh viên đã đăng ký.
- Không xóa lớp đã có sinh viên đăng ký.

### 5.3 Xếp lịch và phân công

Vào menu **Xếp lịch & phân công** (`/app/timetable/manage`).

1. Chọn một lớp trong danh sách bên trái.
2. Điều chỉnh giảng viên, phòng, thứ, tiết, tuần và sĩ số tối đa ở form bên phải.
3. Bấm **Lưu phân công**. Hệ thống kiểm tra xung đột phòng/giảng viên và các ràng buộc trước khi lưu.
4. Nếu có xung đột hoặc dữ liệu không hợp lệ, hệ thống từ chối và hiển thị lý do.

### 5.4 Cấu hình cột điểm

- Mở **Lớp học phần**, bấm **Cấu hình điểm** ở lớp tương ứng.
- Thêm các cột điểm (ví dụ Chuyên cần, Giữa kỳ, Cuối kỳ), nhập trọng số.
- Tổng trọng số phải bằng **100%**.
- Sau khi giảng viên đã nhập điểm, cấu hình bị khóa và không thể sửa.

### 5.5 Quản lý học phí

Vào menu **Quản lý học phí** (`/app/tuition/manage`).

**Xem tổng hợp:**

- Tổng số hóa đơn, tổng phải thu, tổng đã thu, tổng còn nợ của học kỳ.
- Danh sách hóa đơn sinh viên: MSSV, họ tên, khóa, ngành, tổng học phí, phải nộp, đã nộp, còn nợ, trạng thái.
- Tìm theo MSSV và lọc theo trạng thái.

**Phát hành hóa đơn:**

- Bấm **Tính / cập nhật hóa đơn toàn kỳ** để tính học phí cho toàn bộ sinh viên có đăng ký trong học kỳ.
- Hệ thống bỏ qua các hóa đơn đã thanh toán và cập nhật các hóa đơn còn lại.
- Học phí được tính theo số TCHP và đơn giá đang hiệu lực; thanh toán là **một lần cho toàn bộ số còn nợ**.

**Quản lý đơn giá:**

- Chuyển sang tab **Đơn giá học phí**.
- Bấm **Thêm đơn giá** để tạo mức giá mới: đối tượng khóa, ngành áp dụng, đơn giá/TCHP, khoảng hiệu lực, mô tả.
- Đơn giá phải lớn hơn 0; ngày kết thúc phải sau ngày bắt đầu.
- Bấm **Xóa** để xóa đơn giá không còn sử dụng.

**Biên lai:**

- Biên lai được tạo tự động khi sinh viên thanh toán.
- Quản trị viên có thể tra cứu/xem biên lai và tải PDF theo quyền quản trị.

## 6. Xử lý lỗi thường gặp

| Thông báo/mã lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| 401 UNAUTHORIZED / TOKEN_EXPIRED | Chưa đăng nhập hoặc phiên hết hạn | Đăng nhập lại |
| 403 FORBIDDEN | Tài khoản không có quyền với chức năng | Dùng đúng vai trò hoặc liên hệ quản trị viên |
| 400 VALIDATION_ERROR | Dữ liệu nhập thiếu/sai định dạng | Kiểm tra các trường được báo lỗi |
| 404 NOT_FOUND | Không tìm thấy môn/lớp/hóa đơn/biên lai | Kiểm tra lại mã hoặc dữ liệu |
| DUPLICATE_CODE | Mã môn hoặc mã lớp đã tồn tại | Dùng mã khác |
| ALREADY_REGISTERED | Đã đăng ký lớp này | Không cần đăng ký lại |
| SAME_SUBJECT_REGISTERED | Đã đăng ký một lớp khác của cùng môn | Chọn môn khác |
| STUDENT_SCHEDULE_CONFLICT | Lớp trùng lịch với lớp đã đăng ký | Chọn lớp khác hoặc hủy lớp cũ |
| CLASS_FULL | Lớp đã hết chỗ | Chọn lớp khác |
| CREDIT_LIMIT_EXCEEDED | Vượt quá 24 tín chỉ | Bỏ bớt lớp khỏi giỏ |
| CREDIT_LIMIT_BELOW_MIN | Hủy lớp làm tổng tín chỉ dưới 12 | Giữ tối thiểu 12 tín chỉ |
| SCHEDULE_CONFLICT | Phòng hoặc giảng viên trùng lịch | Đổi phòng/giảng viên/thời gian |
| CAPACITY_BELOW_ENROLLMENT | Sĩ số tối đa thấp hơn số đã đăng ký | Tăng sĩ số hoặc không giảm |
| SUBJECT_HAS_SECTIONS | Xóa môn đang có lớp | Xóa các lớp trước |
| SECTION_HAS_REGISTRATIONS | Xóa lớp đang có sinh viên | Không xóa hoặc xử lý đăng ký trước |
| GRADE_COMPONENTS_LOCKED | Đã nhập điểm nên không đổi được cấu hình điểm | Giữ nguyên cấu hình hiện tại |
| INVOICE_NOT_FOUND | Sinh viên chưa có hóa đơn | Quản trị viên phát hành hóa đơn |
| INVOICE_ALREADY_PAID | Hóa đơn đã thanh toán | Không thanh toán lại |
| INVOICE_CANCELLED | Hóa đơn đã bị hủy | Liên hệ quản trị viên |
| TUITION_RATE_NOT_FOUND | Chưa có đơn giá hiệu lực | Quản trị viên thêm đơn giá phù hợp |

## 7. Quy tắc nghiệp vụ cần nhớ

- Một học kỳ duy nhất: **2026.1**.
- Sinh viên phải duy trì **12–24 tín chỉ** trong học kỳ.
- Không đăng ký trùng lớp, trùng môn hoặc trùng lịch.
- Điểm tổng kết làm tròn về **0,5** gần nhất.
- Cấu hình cột điểm bị khóa sau khi đã nhập điểm.
- Học phí thanh toán **một lần cho toàn bộ số còn nợ**, không có đợt nộp và không có miễn giảm.
- Biên lai điện tử có thể xem và tải PDF sau khi thanh toán.
