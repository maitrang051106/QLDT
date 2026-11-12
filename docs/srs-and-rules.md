# Đặc tả Yêu cầu (SRS) & Quy tắc Nghiệp vụ

Tài liệu này hợp nhất đặc tả các ca sử dụng (`UC001–UC010`), phân hệ Học phí & Biên lai điện tử, yêu cầu phi chức năng và toàn bộ quy tắc nghiệp vụ của hệ thống.

---

## 1. Tác nhân hệ thống (Actors)

| Vai trò (`Role`) | Mô tả & Quyền hạn chính |
|---|---|
| **Khách (Public)** | Xem danh mục môn học công khai tại `/catalog` (mã môn, tên môn, số tín chỉ, số lớp mở). |
| **ADMIN** | Quản lý danh mục môn học và lớp học phần (`CRUD`), kiểm tra xung đột lịch toàn trường, cấu hình cột điểm cho từng lớp, xem danh sách sinh viên lớp, quản lý bảng đơn giá học phí, phát hành hóa đơn và xem báo cáo thu học phí. |
| **LECTURER** | Xem lịch giảng dạy theo tuần, xem danh sách các lớp được phân công phụ trách, xem danh sách sinh viên lớp, điểm danh theo ngày học, nhập điểm thành phần và xuất báo cáo Excel (điểm danh & bảng điểm). |
| **STUDENT** | Tra cứu lớp học phần, **Đăng ký lớp** theo giỏ hoặc trực tiếp, hủy đăng ký lớp, xem thời khóa biểu cá nhân theo tuần, xem hóa đơn học phí theo kỳ, thanh toán trực tuyến và tải biên lai điện tử PDF. |

---

## 2. Danh sách Ca sử dụng (Use Cases)

| Mã | Tên chức năng | Tác nhân | Tóm tắt luồng nghiệp vụ chính |
|---|---|---|---|
| **UC001** | Đăng nhập & Phân quyền | Tất cả | Xác thực bằng `username`/`password` trên bảng `USERS` (Bcrypt), cấp JWT `accessToken` sống `3600` giây kèm thông tin `user`. Chặn tài khoản `LOCKED` (`403 ACCOUNT_LOCKED`). |
| **UC002** | Quản lý môn học & lớp học phần | `ADMIN` | Tạo/sửa/xóa môn học (`SUBJECTS`) và lớp học phần (`COURSE_SECTIONS`). Kiểm tra không trùng mã, không trùng lịch phòng hoặc giảng viên cùng thứ/tiết/tuần. Không cho xóa môn đã có lớp hoặc xóa lớp đã có sinh viên/hồ sơ học tập. |
| **UC003** | Xem danh sách SV của lớp (Admin) | `ADMIN` | Từ bảng quản lý lớp học phần (`AdminCatalogPage`), nhấn **"Danh sách SV"** để xem danh sách sinh viên đã đăng ký lớp kèm MSSV, họ tên, email, khóa, ngành và thời điểm đăng ký. |
| **UC004** | Quản lý phiên & quyền sở hữu dữ liệu | `STUDENT`, `LECTURER` | Các endpoint `/me` tự động suy ra định danh sinh viên/giảng viên từ JWT token; chống truy cập chéo tài nguyên của người khác (IDOR). |
| **UC005** | **Đăng ký lớp** | `STUDENT` | Sinh viên chọn các lớp học phần trong kỳ `2026.1` và gửi đăng ký (`POST /api/registrations`). Hệ thống khóa dòng sinh viên (`FOR UPDATE`), kiểm tra chưa đăng ký lớp đó, chưa đăng ký lớp khác của cùng môn, không trùng lịch học, tổng tín chỉ sau đăng ký không vượt `24 TC` (`CREDIT_LIMIT_EXCEEDED`), và cập nhật sĩ số nguyên tử (`current_enrollment < max_capacity`). |
| **UC006** | Hủy đăng ký lớp | `STUDENT` | Sinh viên hủy lớp đã đăng ký của chính mình (`DELETE /api/registrations/{id}`). Nếu sinh viên đang đạt từ `12 TC` trở lên mà việc hủy làm tổng tín chỉ tụt xuống dưới `12 TC`, hệ thống từ chối với mã `CREDIT_LIMIT_BELOW_MIN`. Khi hủy thành công, hệ thống giảm `current_enrollment` đi 1 và xóa các bản ghi điểm danh/điểm thành phần lẻ chưa chốt của sinh viên đó trong lớp. |
| **UC007** | Xem thời khóa biểu sinh viên | `STUDENT` | Xem lịch học theo từng tuần (`1..numWeeks`) của học kỳ hiện tại (`2026.1`), tự động tính ngày cụ thể (`yyyy-MM-dd`) cho từng buổi học. |
| **UC008** | Xem lịch giảng dạy giảng viên | `LECTURER` | Xem lịch dạy theo tuần và danh sách các lớp học phần được phân công giảng dạy trong kỳ `2026.1`. |
| **UC009** | Xem danh sách SV của lớp (Giảng viên) | `LECTURER` | Giảng viên xem danh sách sinh viên của lớp do chính mình phụ trách (từ chối `403 FORBIDDEN` nếu truy cập lớp của giảng viên khác). |
| **UC010** | Điểm danh, Bảng điểm & Xuất Excel | `LECTURER`, `ADMIN` | `ADMIN` cấu hình 1–10 cột điểm cho lớp (tổng trọng số = `100%`, khóa cấu hình khi đã có điểm). `LECTURER` phụ trách lớp điểm danh (`PRESENT`, `ABSENT`, `LATE`, `EXCUSED`) đúng ngày học trong lịch, nhập điểm từng cột và xuất file `.xlsx` gồm sheet Điểm danh & Bảng điểm. |
| **Học phí** | Học phí & Biên lai điện tử | `STUDENT`, `ADMIN` | `ADMIN` cấu hình bảng đơn giá (`TUITION_RATES`) theo Khóa/Ngành, phát hành hóa đơn (`TUITION_INVOICES`). `STUDENT` xem hóa đơn, thanh toán một lần toàn bộ số tiền phải nộp (chống trùng lặp bằng `idempotencyKey`), xem danh sách hóa đơn đã nộp và tải biên lai PDF (`RECEIPTS`). |

---

## 3. Quy tắc Nghiệp vụ Cốt lõi (Business Rules)

1. **Một học kỳ hoạt động duy nhất (`2026.1`)**:
   - Hệ thống không phân mảnh dữ liệu theo nhiều học kỳ. Mọi nghiệp vụ đăng ký lớp, thời khóa biểu, điểm danh, bảng điểm và học phí đều vận hành trên học kỳ hiện tại `2026.1`.
2. **Loại bỏ các tính năng ngoài phạm vi**:
   - Không kiểm tra học phần tiên quyết hay học phần song hành.
   - Không sử dụng API đổi lớp nguyên tử (`PUT /api/registrations/{id}/change`) hay API gợi ý thời khóa biểu tự động.
   - Không áp dụng nghiệp vụ miễn giảm học phí (`TUITION_DISCOUNTS`); số tiền phải nộp (`amount_due`) bằng đúng tổng học phí các môn đã đăng ký (`total_tuition`).
3. **Sĩ số và Giới hạn Tín chỉ (`12–24 TC`)**:
   - `current_enrollment` không bao giờ vượt quá `max_capacity`.
   - Tổng tín chỉ học kỳ của sinh viên bằng tổng `SUBJECTS.credits` của các lớp đã đăng ký.
   - Cấu hình mặc định toàn hệ thống: tối thiểu `MIN_CREDITS_PER_SEMESTER=12`, tối đa `MAX_CREDITS_PER_SEMESTER=24`.
4. **Quy tắc Kiểm tra Xung đột Lịch (`ConflictEngine`)**:
   - Hai lớp học phần bị coi là trùng lịch nếu cùng `day_of_week`, khoảng tiết `[start_period, end_period]` giao nhau **và** khoảng tuần `[start_week, end_week]` giao nhau.
   - Áp dụng thống nhất cho cả 3 đối tượng: Sinh viên (`STUDENT`), Phòng học (`ROOM`) và Giảng viên (`LECTURER`).
5. **Quy tắc Tính điểm & Học phí**:
   - Điểm tổng kết lớp học phần chỉ được tính khi sinh viên đã có đủ điểm ở tất cả các cột điểm thành phần: quy đổi từng cột về thang 10 (`score / max_score * 10`), nhân trọng số (`weight_percentage / 100`), cộng tổng và làm tròn đến mức `0.5` gần nhất (`0.25` làm tròn lên `0.5`).
   - Học phí từng môn tính bằng `int(Decimal(tuition_credits) * Decimal(price_per_credit))` (làm tròn xuống đến đồng, tuyệt đối không dùng số thực dấu phẩy động `float`).
   - Học phí chỉ thanh toán **một lần** đúng bằng số còn phải nộp (`amount_due - amount_paid`); không chia đợt nộp và không nộp một phần.
