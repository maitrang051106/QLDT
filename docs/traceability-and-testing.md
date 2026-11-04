# Truy vết Yêu cầu, Tiến độ & Kiểm thử Hệ thống

Tài liệu này hợp nhất ma trận truy vết (`Traceability Matrix`), bảng trạng thái công việc (`Work Board`) và hướng dẫn kiểm thử tự động / tích hợp của dự án.

---

## 1. Ma trận Truy vết (Traceability Matrix)

| Yêu cầu / Ca sử dụng | Endpoint API (`/api/*`) | Đường dẫn Frontend | Trạng thái & Kiểm thử |
|---|---|---|---|
| **UC001** Đăng nhập & RBAC | `POST /auth/login`, `GET /auth/me`, `POST /auth/logout` | `/login`, khung phân quyền theo vai trò | **Hoàn thành** — Đã kiểm thử xác thực JWT, mật khẩu Bcrypt, khóa tài khoản và phân quyền RBAC (`test_auth.py`, `test_rbac.py`). |
| **UC002** Quản lý môn học & lớp học phần | `/subjects`, `/sections`, `/sections/lookups` | `/catalog`, `/app/subjects`, `/app/sections` | **Hoàn thành** — Đã kiểm thử CRUD môn/lớp, kiểm tra trùng lịch phòng/giảng viên và ràng buộc xóa (`test_admin_training.py`). |
| **UC003** Xem danh sách SV lớp (Admin) | `GET /sections/{id}/students` | `/app/sections/:sectionId/students` (nút **"Danh sách SV"** từ `AdminCatalogPage`) | **Hoàn thành** — Admin điều hướng trực tiếp từ bảng lớp học phần sang danh sách sinh viên của lớp. |
| **UC004** Phiên sinh viên & Chống IDOR | JWT, các API `/me` | Route guard & bộ lọc quyền sở hữu | **Hoàn thành** — Kiểm thử chống truy cập chéo dữ liệu người khác (`test_concurrency_and_security.py`). |
| **UC005** **Đăng ký lớp** | `GET /sections`, `POST /registrations`, `GET /registrations/me` | `/app/sections` | **Hoàn thành** — Giỏ lớp học phần, kiểm tra trùng môn/trùng lịch, giới hạn tối đa `24 TC` và chống vượt sĩ số đồng thời (`test_registration.py`, `test_concurrency_and_security.py`). |
| **UC006** Hủy đăng ký lớp | `DELETE /registrations/{id}` | `/app/registrations` | **Hoàn thành** — Kiểm tra quyền sở hữu, giới hạn tối thiểu `12 TC` (`CREDIT_LIMIT_BELOW_MIN`), giảm sĩ số nguyên tử và dọn bản ghi điểm danh/điểm lẻ (`test_registration.py`). |
| **UC007** Thời khóa biểu sinh viên | `GET /semesters/current`, `GET /students/me/timetable` | `/app/timetable` | **Hoàn thành** — Hiển thị lịch học theo tuần trên kỳ duy nhất `2026.1`. |
| **UC008** Lịch giảng dạy giảng viên | `GET /semesters/current`, `GET /lecturers/me/timetable`, `GET /lecturers/me/sections` | `/app/timetable`, `/app/sections` | **Hoàn thành** — Hiển thị lịch dạy theo tuần và danh sách lớp phụ trách. |
| **UC009** Xem danh sách SV lớp (Giảng viên) | `GET /lecturers/me/sections`, `GET /sections/{id}/students` | `/app/sections/:sectionId/students` | **Hoàn thành** — Kiểm tra đúng giảng viên phụ trách lớp trước khi trả danh sách sinh viên. |
| **UC010** Điểm danh, Bảng điểm & Xuất Excel | `/sections/{id}/attendance`, `/sections/{id}/grades`, `/sections/{id}/grade-components`, `/sections/{id}/exports/*` | `/app/sections/:sectionId/students` (Giảng viên); `/app/sections` (Admin cấu hình cột điểm) | **Hoàn thành** — Kiểm thử đầy đủ điểm danh đúng ngày học, khóa cấu hình cột điểm, tính điểm tổng kết làm tròn `0.5` và xuất file `.xlsx` (`test_academic_records.py`). |
| **Xung đột lịch học** | `POST /timetable/check` | `/app/admin/timetable`, `/app/sections` | **Hoàn thành** — Phát hiện xung đột `STUDENT`, `ROOM`, `LECTURER` theo thứ/tiết/tuần (`test_timetable_conflicts.py`). |
| **Học phí & Biên lai điện tử** | `/tuition/me`, `/tuition/me/payments`, `/receipts/*`, `/admin/tuition-rates`, `/admin/tuition/*` | `/app/tuition` (Sinh viên), `/app/tuition/manage` (Admin) | **Hoàn thành** — Tính học phí theo TCHP, cấu hình đợt nộp, thanh toán idempotent, xuất PDF biên lai và báo cáo tổng hợp (`test_tuition_api.py`, `test_tuition_calculation.py`). |

---

## 2. Tổng hợp Kiểm thử & Đảm bảo Chất lượng

### Kiểm thử đơn vị & API trên SQLite (`pytest backend/tests`)
- Chạy tự động hoàn toàn trong bộ nhớ mà không cần MySQL bên ngoài.
- Bao phủ:
  - Xác thực, phân quyền RBAC và bảo mật chống IDOR / rò rỉ `password_hash`.
  - Tranh chấp đăng ký đồng thời (`concurrency race`) khi nhiều sinh viên cùng抢 1 chỗ trống cuối cùng.
  - Quy tắc tín chỉ `12–24 TC`, trùng lịch học và dọn dẹp hồ sơ học tập khi hủy đăng ký.
  - Điểm danh, cấu hình cột điểm, tính điểm tổng kết và xuất Excel.
  - Tính học phí theo TCHP, phân bổ đợt nộp, thanh toán idempotent và kết xuất file PDF biên lai.

### Kiểm thử tích hợp MySQL & Gateway (`pytest -m integration` & `gateway/smoke_test.py`)
- Kiểm tra lược đồ Alembic khớp 100% với ORM Entity (`alembic upgrade head && alembic check`).
- Kiểm tra `gateway/smoke_test.py` qua cổng `http://localhost:8080`:
  - `/health` của Gateway trả `200` kèm header `X-Request-Id` và ẩn phiên bản Nginx.
  - `/health/backend` kết nối thông suốt tới FastAPI.
  - `/` trả về giao diện SPA của Frontend (`<div id="root">`).
  - `/api/auth/me` và `/api/auth/login` chuyển tiếp nguyên vẹn mã lỗi chuẩn của Backend.

### Kiểm thử hiệu năng & Chịu tải cổng đăng ký (`tests/performance/registration-load.js`)
- Sử dụng công cụ `k6` độc lập để đo tải end-to-end qua API Gateway (`http://localhost:8080`).
- Kịch bản đo tải:
  - `MODE=read`: Nhiều sinh viên ảo (VUs) cùng lúc tra cứu danh mục lớp học phần (`GET /api/sections`) và danh sách lớp đã đăng ký (`GET /api/registrations/me`).
  - `MODE=cycle`: Thực hiện chu trình hoàn chỉnh gồm đăng nhập $\rightarrow$ đăng ký lớp (`POST /api/registrations`) $\rightarrow$ xác thực giỏ môn $\rightarrow$ hủy đăng ký (`DELETE /api/registrations/{id}`) nhằm đánh giá độ trễ (`p(95) < 2000ms`) và tỷ lệ thành công khi tranh chấp ghi.
