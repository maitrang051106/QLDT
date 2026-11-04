# Quy tắc Kiến trúc & Nghiệp vụ Backend

- **Nền tảng**: Python 3.12+, FastAPI, SQLAlchemy 2, Alembic; thư mục gốc của ứng dụng là `backend/app/`.
- **Chạy local**: `uvicorn app.main:app --reload` từ thư mục `backend/`.
- **Xác thực**: Đọc trực tiếp từ bảng `USERS` trong MySQL; code chạy thật tuyệt đối không dùng tài khoản giả lập (mock/fixture).
- **Nguồn chuẩn CSDL**: `db/schema.sql` và `db/seed/seed.sql` (18 bảng). Các Entity ORM và Alembic migration phải giữ nguyên tên bảng viết hoa (`UPPER_SNAKE_CASE`) trên cơ sở dữ liệu `qldt`.
- **Bảo mật & Cấu hình**:
  - `JWT_SECRET` bắt buộc có độ dài tối thiểu 32 ký tự; thời hạn `accessToken` là `3600` giây (không dùng refresh token).
  - Giới hạn tín chỉ học kỳ được cấu hình qua biến môi trường hệ thống (`MIN_CREDITS_PER_SEMESTER=12`, `MAX_CREDITS_PER_SEMESTER=24`).
- **Học kỳ duy nhất & Đồng thời (Concurrency)**:
  - Toàn hệ thống chỉ vận hành trên 1 học kỳ đang mở đăng ký duy nhất (`2026.1`); các API tự động lấy học kỳ này nếu client không truyền `semesterId`.
  - Đăng ký lớp (`POST /api/registrations`) và hủy đăng ký (`DELETE /api/registrations/{id}`) khóa dòng sinh viên bằng `SELECT ... FOR UPDATE` và cập nhật sĩ số nguyên tử có điều kiện (`current_enrollment < max_capacity`).
  - Khi sinh viên hủy đăng ký lớp, hệ thống kiểm tra quy tắc tối thiểu `12 TC` (`CREDIT_LIMIT_BELOW_MIN`) và tự động dọn dẹp các bản ghi điểm danh/điểm thành phần lẻ của sinh viên đó trong lớp vừa hủy.
  - Không áp dụng điều kiện học phần tiên quyết, học phần song hành, API đổi lớp nguyên tử (`PUT /registrations/{id}/change`), gợi ý thời khóa biểu tự động hay miễn giảm học phí.
- **Cấu trúc phân tầng**:
  - Mã nguồn nghiệp vụ đặt tại `app/{controller,service,repository,entity,dto}/{auth,catalog,registration,timetable,tuition}`.
  - Cấu hình và mã lỗi dùng chung đặt tại `app/core/`; bảo mật JWT/RBAC đặt tại `app/security/`.
- **Hồ sơ học tập (UC010)**:
  - Chỉ giảng viên được phân công phụ trách lớp mới có quyền xem/lưu điểm danh, nhập điểm và xuất file Excel cho lớp đó.
  - `ADMIN` cấu hình từ 1–10 cột điểm cho từng lớp với tổng trọng số đúng bằng `100%`; cấu trúc điểm bị khóa sau khi giảng viên đã nhập điểm. Điểm tổng kết chỉ tính khi đủ mọi cột điểm, quy đổi về thang 10 và làm tròn đến `0.5` gần nhất.
- **Học phí & Biên lai**:
  - Tính học phí theo `tuition_credits` (TCHP) nhân với đơn giá hiệu lực (`TUITION_RATES`) theo thứ tự ưu tiên: `Khóa + Ngành` -> `Khóa` -> `Ngành` -> `Chung toàn trường`.
  - Hỗ trợ cấu hình các đợt nộp (`TUITION_INSTALLMENTS`), thanh toán trực tuyến idempotent theo `idempotencyKey` và phát hành biên lai điện tử kèm tải PDF từ dữ liệu snapshot bất biến (`RECEIPTS`).

## Bộ kiểm thử trọng tâm

- `pytest backend/tests/test_concurrency_and_security.py` — Kiểm thử tranh chấp sĩ số đồng thời, chống IDOR, chống rò rỉ mật khẩu và leo thang đặc quyền.
- `pytest backend/tests/test_registration.py` — Kiểm thử đăng ký lớp, hủy đăng ký, giới hạn `12–24 TC` và dọn dẹp dữ liệu điểm danh/điểm khi hủy.
- `pytest backend/tests/test_academic_records.py` — Kiểm thử điểm danh, bảng điểm, quyền giảng viên phụ trách và xuất báo cáo Excel.
- `pytest backend/tests/test_tuition_api.py backend/tests/test_tuition_calculation.py` — Kiểm thử đơn giá, đợt nộp, phát hành hóa đơn, thanh toán idempotent và xuất PDF biên lai.
