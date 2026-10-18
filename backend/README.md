# Backend – Hệ thống Quản lý & Đăng ký Học phần (Nhóm 20)

Python 3.12 · FastAPI · SQLAlchemy 2.0 · Alembic · MySQL 8 · JWT + Bcrypt.
Bám theo *Tài liệu thiết kế phần mềm* (kiến trúc, CSDL, lớp) và *Quy ước API & JSON FE–BE*
(`openapi.yaml` là bản đúng nếu có mâu thuẫn).

## Chạy lần đầu (VS Code)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows;  macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env          # macOS/Linux: cp .env.example .env  (rồi đổi JWT_SECRET)

docker compose up -d db         # MySQL; hoặc tự cài MySQL rồi sửa DATABASE_URL trong .env
alembic upgrade head            # tạo schema từ migration ban đầu đã có
python -m scripts.seed          # tài khoản mẫu: admin / gv001 / sv20260001
uvicorn app.main:app --reload   # hoặc F5 với cấu hình "API: uvicorn (reload)"
```

Swagger UI: http://localhost:8000/api/docs · Health: http://localhost:8000/health
Test: `pytest` (dùng SQLite trong bộ nhớ, không cần MySQL).
Lint/format: `ruff check .` · `ruff format .`

Khi thay đổi schema: chạy `alembic revision --autogenerate -m "mô tả thay đổi"`, kiểm tra migration,
chạy `alembic upgrade head`, rồi commit file trong `migrations/versions/`. CI kiểm tra migration
trên MySQL thật; deploy cũng chạy migration trước khi khởi động phiên bản backend mới.

## Cấu trúc: 5 tầng × 4 module (mục 2.2 tài liệu thiết kế)

```
app/
├─ controller/   auth · catalog · registration · timetable   (nhận request, gọi Service, trả DTO)
├─ service/      auth · catalog · registration · timetable   (nghiệp vụ + ranh giới giao dịch)
├─ repository/   auth · catalog · registration               (truy cập CSDL, không commit)
├─ entity/       auth · catalog · registration               (8 bảng; timetable không có entity riêng)
├─ dto/          auth · catalog · registration · timetable   (JSON vào/ra, camelCase)
├─ security/     jwt_provider · password · dependencies      (JwtAuthFilter, RoleChecker, Bcrypt)
├─ core/         config · database · error_codes · exceptions · error_handlers · timeutil
└─ main.py
```

Phụ thuộc chỉ đi một chiều: `controller → service → repository → entity`.
Controller không chứa nghiệp vụ; Repository không chứa quy tắc nghiệp vụ và không `commit()`.

## Quy ước đã cài sẵn

| Chủ đề | Cách làm |
|---|---|
| Tên trường JSON | `CamelModel` (dto/common.py): viết snake_case trong code, JSON là camelCase |
| Danh sách | `ItemList[T]` → `{items}`; `Page[T]` → thêm `page,size,totalItems,totalPages` |
| Lỗi | Ném `AppError(ErrorCode.X, details=[field_error(...)])` → `ErrorResponse` (status, error, message, details, path, timestamp). Đủ 17 mã lỗi trong `core/error_codes.py` |
| Lỗi validation | Tự đổi thành `VALIDATION_ERROR` + `details[].field` camelCase, message tiếng Việt |
| Xác thực | `Authorization: Bearer <JWT>`, sống 3600 s, không refresh |
| Phân quyền lớp 1 | Khai báo kiểu tham số: `user: AdminUser`, `StudentUser`, `LecturerUser`, `AdminOrStudent`, `AdminOrLecturer`, `CurrentUser` |
| Phân quyền lớp 2 | Service kiểm tra quyền sở hữu (sinh viên chỉ hủy đăng ký của mình, GV chỉ xem lớp mình phụ trách) |
| Giao dịch | Một use case = một `db.commit()` ở cuối Service; lỗi bất kỳ → `get_db` rollback |
| Ngày giờ | CSDL lưu giờ VN naive; JSON ra `+07:00` (`VNDateTime`) |
| `id` người dùng | Luôn lấy từ token, không nhận `studentId`/`lecturerId` từ client |

## Thêm một chức năng: làm theo thứ tự

1. DTO (đã có đủ theo từ điển dữ liệu) → 2. Repository (truy vấn) → 3. Service (nghiệp vụ, ném `AppError`)
→ 4. Controller (đã nối sẵn route + quyền) → 5. Viết test trong `tests/`.

## Hiện trạng

**Đã chạy được:** `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`,
`GET /api/semesters`, `GET /api/semesters/current`, `GET /health`, Security Filter + RBAC, xử lý lỗi chung.

**Còn là khung (trả `501 NOT_IMPLEMENTED`)** – mỗi hàm Service có docstring ghi sẵn quy tắc và thứ tự kiểm tra:

- `SubjectService` (5 endpoint môn học) và `SubjectRepository`
- `SectionService` (CRUD lớp, lookups, danh sách sinh viên) và phần `search/list` của `SectionRepository`
- `RegistrationService` (đăng ký, hủy, đăng ký của tôi) và `list_*` của `RegistrationRepository`
- `TimetableService` (thời khóa biểu sinh viên / giảng viên, lớp phụ trách)

**Đã viết sẵn các truy vấn khó theo mục 3.3:** tăng/giảm sĩ số nguyên tử
(`SectionRepository.increment_enrollment_if_available`), xung đột phòng/giảng viên
(`find_room_or_lecturer_conflicts`), trùng môn / trùng lịch của sinh viên (`RegistrationRepository`).

## Việc nối tiếp (ngoài thư mục này)

- API Gateway: sẽ đặt ở `gateway/`, định tuyến `/api/*` về `backend:8000` (docs cũng nằm dưới `/api`).
- CI/CD: `.github/workflows/` (ruff → pytest → build Docker image).
- Chuyển `docker-compose.yml` lên thư mục gốc repo khi có thêm `gateway/` và `frontend/`.

## Điểm cần nhóm chốt (từ mục 9 tài liệu quy ước)

Chưa có API tạo/khóa tài khoản (đang nạp sẵn bằng `scripts/seed.py`); bảng quy đổi tiết → giờ
do FE hay BE trả; danh sách sinh viên của lớp hiện không phân trang.
