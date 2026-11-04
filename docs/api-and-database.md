# Quy ước API FE–BE & Thiết kế Cơ sở dữ liệu

Tài liệu này hợp nhất quy ước giao tiếp HTTP/JSON, bảng mã lỗi nghiệp vụ, ánh xạ tên trường và thiết kế lược đồ cơ sở dữ liệu MySQL (18 bảng). Nguồn schema máy đọc được cuối cùng là `contracts/openapi.yaml`, `contracts/api-types.ts` và `db/schema.sql`.

---

## 1. Quy ước JSON, HTTP & Xác thực

- **Đường dẫn gốc**: Tất cả endpoint nghiệp vụ dùng tiền tố `/api` (không đánh số version). Endpoint kiểm tra sức khỏe hệ thống đặt tại `/health`.
- **Định dạng JSON**:
  - Khóa JSON dùng `camelCase`; giá trị enum dùng `UPPER_SNAKE_CASE`.
  - Trường không có giá trị trả về `null`, không tự ý lược bỏ trường khỏi object.
  - Danh sách không phân trang bọc trong `{ "items": [...] }`.
  - Danh sách có phân trang (`subjects`, `sections`, `admin/tuition/invoices`) nhận query `page`, `size`, `sort` và trả về `{ "items": [...], "page": 1, "size": 20, "totalItems": ..., "totalPages": ... }`.
  - Ngày dùng định dạng `yyyy-MM-dd`; ngày giờ dùng ISO 8601 có múi giờ Việt Nam `+07:00`.
- **Khóa ngoại & Object lồng nhau**:
  - Khi gửi request ghi (`POST`/`PUT`), truyền khóa ngoại dạng `subjectId`, `semesterId`, `lecturerId`, `roomId`, `sectionId`.
  - Khi đọc response (`GET`), các thực thể chính (`subject`, `section`, `semester`, `registration`) trả khóa chính tên là `id` và có thể đính kèm object con (`subject`, `semester`, `lecturer`, `room`).
- **Xác thực JWT**:
  - `POST /api/auth/login` trả `{ accessToken, tokenType: "Bearer", expiresIn: 3600, user }`.
  - Client gửi header `Authorization: Bearer <accessToken>` trong các request tiếp theo.

---

## 2. Cấu trúc Phản hồi Lỗi & Bảng Mã lỗi (`ErrorCode`)

Mọi lỗi nghiệp vụ và xác thực đều trả về cùng cấu trúc `ErrorResponse`:

```json
{
  "status": 409,
  "error": "CREDIT_LIMIT_BELOW_MIN",
  "message": "Không thể hủy vì số tín chỉ sẽ thấp hơn mức tối thiểu",
  "details": [
    { "field": "credits", "message": "Số tín chỉ hiện tại: 12, sau khi hủy: 9, tối thiểu cần: 12" }
  ],
  "path": "/api/registrations/15",
  "timestamp": "2026-11-04T17:30:00+07:00"
}
```

> **Quy tắc phía Frontend**: Luôn rẽ nhánh xử lý theo trường `error`, không bao giờ so khớp chuỗi `message`.

| Mã lỗi (`error`) | HTTP | Ý nghĩa & Hành vi xử lý trên UI |
|---|---:|---|
| `VALIDATION_ERROR` | 400 | Dữ liệu đầu vào không hợp lệ; gắn `details[].field` vào từng ô nhập trên form. |
| `INVALID_WEEK` | 400 | Tuần truy vấn nằm ngoài phạm vi `1..numWeeks` của học kỳ. |
| `INSTALLMENT_SUM_MISMATCH` | 400 | Tổng tỷ lệ phần trăm các đợt nộp khác `100%` hoặc trộn lẫn phần trăm và số tiền cố định. |
| `UNAUTHORIZED`, `TOKEN_EXPIRED` | 401 | Chưa đăng nhập hoặc token hết hạn; xóa phiên và chuyển về `/login`. |
| `INVALID_CREDENTIALS` | 401 | Sai tên đăng nhập hoặc mật khẩu. |
| `ACCOUNT_LOCKED` | 403 | Tài khoản đã bị khóa. |
| `FORBIDDEN` | 403 | Không đủ quyền truy cập tài nguyên; hiển thị thông báo lỗi, **không** đăng xuất. |
| `NOT_FOUND` | 404 | Không tìm thấy bản ghi yêu cầu. |
| `TUITION_RATE_NOT_FOUND` | 404 | Học kỳ chưa được cấu hình đơn giá học phí phù hợp. |
| `INVOICE_NOT_FOUND` | 404 | Không tìm thấy hóa đơn học phí của sinh viên. |
| `DUPLICATE_CODE` | 409 | Trùng mã môn học, mã lớp học phần hoặc trùng khoảng hiệu lực đơn giá. |
| `SCHEDULE_CONFLICT` | 409 | Trùng lịch phòng học hoặc giảng viên khi tạo/cập nhật lớp học phần. |
| `SUBJECT_HAS_SECTIONS` | 409 | Không thể xóa môn học đã có lớp học phần. |
| `SECTION_HAS_REGISTRATIONS` | 409 | Không thể xóa lớp học phần đã có sinh viên đăng ký. |
| `SECTION_HAS_ACADEMIC_RECORDS` | 409 | Không thể xóa lớp học phần đã có dữ liệu điểm danh hoặc cấu hình cột điểm. |
| `CAPACITY_BELOW_ENROLLMENT` | 409 | Không thể giảm `maxCapacity` xuống thấp hơn `currentEnrollment` hiện tại. |
| `GRADE_COMPONENTS_LOCKED` | 409 | Không thể sửa cấu trúc cột điểm sau khi giảng viên đã nhập điểm. |
| `CLASS_FULL` | 409 | Lớp học phần đã đủ sĩ số; gọi `refetch` lại danh sách lớp. |
| `ALREADY_REGISTERED` | 409 | Sinh viên đã đăng ký lớp học phần này. |
| `SAME_SUBJECT_REGISTERED` | 409 | Sinh viên đã đăng ký một lớp khác của cùng môn học trong học kỳ. |
| `STUDENT_SCHEDULE_CONFLICT` | 409 | Lớp đăng ký bị trùng lịch học với lớp đã đăng ký trước đó. |
| `CREDIT_LIMIT_EXCEEDED` | 409 | Tổng số tín chỉ vượt quá mức tối đa (`24 TC`). |
| `CREDIT_LIMIT_BELOW_MIN` | 409 | Không thể hủy lớp vì sẽ làm tổng tín chỉ tụt xuống dưới mức tối thiểu (`12 TC`). |
| `INVOICE_ALREADY_PAID` | 409 | Hóa đơn đã được nộp đủ tiền. |
| `PAYMENT_EXCEEDS_BALANCE` | 409 | Số tiền nộp vượt quá số dư còn nợ của hóa đơn hoặc của đợt nộp đã chọn. |
| `INVOICE_HAS_PAYMENTS` | 409 | Đã có giao dịch thanh toán, không thể thay đổi cấu hình đợt nộp hoặc tính lại hóa đơn. |
| `INVOICE_CANCELLED` | 409 | Hóa đơn đã bị hủy, không nhận thanh toán. |
| `INTERNAL_ERROR` | 500 | Lỗi hệ thống ngoài dự kiến; hiển thị thông báo thân thiện, không lộ chi tiết kỹ thuật. |

---

## 3. Danh mục Endpoint Chính (`/api`)

| Nhóm | Method & Đường dẫn | Quyền truy cập | Mô tả |
|---|---|---|---|
| **Auth** | `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout` | Công khai / Đã đăng nhập | Đăng nhập, lấy thông tin tài khoản hiện tại, đăng xuất. |
| **Catalog** | `GET /api/subjects`, `POST/PUT/DELETE /api/subjects/{id}` | Công khai (`GET`) / `ADMIN` | Tra cứu công khai và quản lý danh mục môn học. |
| **Sections** | `GET /api/sections`, `GET /api/sections/lookups`, `POST/PUT/DELETE /api/sections/{id}` | Đã đăng nhập / `ADMIN` | Tra cứu lớp học phần (kèm `remainingSeats`, `full`, `registeredByMe`) và quản lý lớp. |
| **Roster** | `GET /api/sections/{id}/students` | `ADMIN` / `LECTURER` phụ trách | Xem danh sách sinh viên đã đăng ký vào lớp học phần. |
| **Semester** | `GET /api/semesters`, `GET /api/semesters/current` | Đã đăng nhập | Trả về học kỳ duy nhất đang mở (`2026.1`) và tuần học hiện tại (`currentWeek`). |
| **Registration** | `POST /api/registrations`, `DELETE /api/registrations/{id}`, `GET /api/registrations/me` | `STUDENT` | **Đăng ký lớp**, hủy đăng ký của chính mình và xem danh sách lớp đã đăng ký. |
| **Timetable** | `GET /api/students/me/timetable`, `GET /api/lecturers/me/timetable`, `GET /api/lecturers/me/sections`, `POST /api/timetable/check` | `STUDENT` / `LECTURER` / Đã đăng nhập | Xem thời khóa biểu theo tuần và kiểm tra xung đột lịch học. |
| **Academic (UC010)** | `GET/PUT /api/sections/{id}/attendance`, `GET/PUT /api/sections/{id}/grades`, `GET/PUT /api/sections/{id}/grade-components`, `GET /api/sections/{id}/exports/{attendance,grades}` | `LECTURER` phụ trách / `ADMIN` (cấu hình cột điểm) | Điểm danh theo ngày học, cấu hình cột điểm, nhập bảng điểm và xuất báo cáo Excel (`.xlsx`). |
| **Tuition** | `GET /api/tuition/me`, `POST /api/tuition/me/payments`, `GET /api/receipts/me`, `GET /api/receipts/{id}`, `GET /api/receipts/{id}/pdf` | `STUDENT` (`ADMIN` xem được biên lai) | Sinh viên xem hóa đơn, nộp học phí idempotent và xem/tải biên lai điện tử PDF. |
| **Tuition Admin** | `GET/POST/PUT/DELETE /api/admin/tuition-rates`, `GET/PUT /api/admin/tuition/installments`, `POST /api/admin/tuition/invoices/generate`, `GET /api/admin/tuition/invoices`, `GET /api/admin/tuition/reports/summary` | `ADMIN` | Quản lý bảng đơn giá, cấu hình đợt nộp, phát hành hóa đơn hàng loạt và xem báo cáo tổng hợp. |

---

## 4. Thiết kế Cơ sở Dữ liệu (`db/schema.sql` – 18 bảng)

Toàn bộ khóa ngoại sử dụng `ON UPDATE CASCADE ON DELETE RESTRICT`. Tên bảng và cột dùng `UPPER_SNAKE_CASE`.

### Nhóm 1: Tài khoản & Danh mục Đào tạo (8 bảng)
1. `USERS`: Tài khoản đăng nhập (`user_id`, `username`, `password_hash`, `full_name`, `email`, `role` [`ADMIN`/`LECTURER`/`STUDENT`], `status` [`ACTIVE`/`LOCKED`]).
2. `STUDENTS`: Hồ sơ sinh viên (`student_id`, `user_id`, `student_code`, `cohort`, `major`).
3. `LECTURERS`: Hồ sơ giảng viên (`lecturer_id`, `user_id`, `lecturer_code`, `department`).
4. `SUBJECTS`: Môn học (`subject_id`, `subject_code`, `name`, `credits`, `tuition_credits`, `description`).
5. `SEMESTERS`: Học kỳ (`semester_id`, `semester_code`, `name`, `start_date`, `end_date`, `num_weeks`).
6. `ROOMS`: Phòng học (`room_id`, `room_code`, `building`, `capacity`).
7. `COURSE_SECTIONS`: Lớp học phần (`section_id`, `section_code`, `subject_id`, `semester_id`, `lecturer_id`, `room_id`, `day_of_week` [2..8], `start_period` [1..12], `end_period` [1..12], `start_week`, `end_week`, `max_capacity`, `current_enrollment`).
8. `REGISTRATIONS`: Bản ghi đăng ký lớp của sinh viên (`registration_id`, `student_id`, `section_id`, `registered_at`; khóa duy nhất `(student_id, section_id)`).

### Nhóm 2: Điểm danh & Bảng điểm – UC010 (3 bảng)
9. `ATTENDANCE_RECORDS`: Điểm danh theo buổi học (`attendance_id`, `section_id`, `student_id`, `class_date`, `status` [`PRESENT`/`ABSENT`/`LATE`/`EXCUSED`], `recorded_by_user_id`; duy nhất theo `(section_id, student_id, class_date)`).
10. `SECTION_GRADE_COMPONENTS`: Cấu hình cột điểm của lớp (`component_id`, `section_id`, `name`, `weight_percentage`, `max_score`, `sort_order`).
11. `STUDENT_GRADES`: Điểm từng cột của sinh viên (`grade_id`, `component_id`, `student_id`, `score`, `updated_by_user_id`; duy nhất theo `(component_id, student_id)`).

### Nhóm 3: Học phí & Biên lai Điện tử (7 bảng)
12. `TUITION_RATES`: Bảng đơn giá 1 TCHP theo học kỳ, khóa, ngành và khoảng ngày hiệu lực (`rate_id`, `semester_id`, `cohort`, `major`, `effective_from`, `effective_to`, `price_per_credit`).
13. `TUITION_INSTALLMENTS`: Cấu hình các đợt nộp trong học kỳ (`installment_id`, `semester_id`, `installment_order`, `name`, `due_date`, `percentage`, `fixed_amount`).
14. `TUITION_INVOICES`: Hóa đơn học phí của sinh viên theo kỳ (`invoice_id`, `student_id`, `semester_id`, `total_tuition`, `amount_due`, `amount_paid`, `status` [`UNPAID`/`PARTIALLY_PAID`/`PAID`/`CANCELLED`], `is_stale`).
15. `TUITION_INVOICE_ITEMS`: Snapshot chi tiết từng môn học trong hóa đơn (`item_id`, `invoice_id`, `subject_id`, `subject_code`, `subject_name`, `credits`, `tuition_credits`, `price_per_credit`, `amount`).
16. `TUITION_PAYMENTS`: Giao dịch nộp học phí (`payment_id`, `invoice_id`, `student_id`, `installment_id`, `amount`, `idempotency_key`, `payment_method`, `paid_at`; duy nhất theo `(student_id, idempotency_key)`).
17. `RECEIPTS`: Biên lai điện tử phát hành cho mỗi lần thanh toán (`receipt_id`, `receipt_no`, `payment_id`, `student_id`, `invoice_id`, `amount`, `issued_at`, `receipt_data` JSON bất biến).
18. `RECEIPT_SEQUENCES`: Bộ đếm cấp số biên lai tuần tự theo học kỳ (`semester_id`, `current_number`).
