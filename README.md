# QLDT — Hệ thống Quản lý và Đăng ký Học phần

Dự án môn học IT3180 (Nhóm 20). Công nghệ sử dụng: **React 19 + TypeScript + Ant Design**, **FastAPI + SQLAlchemy 2 + Alembic**, **MySQL 8.4** và **Nginx API Gateway**.

Hệ thống vận hành tập trung trên **1 học kỳ đăng ký duy nhất (`2026.1`)**, bao gồm các phân hệ:
- Xác thực & phân quyền JWT (`ADMIN`, `LECTURER`, `STUDENT`).
- Quản lý danh mục môn học, lớp học phần và kiểm tra xung đột lịch phòng / giảng viên / sinh viên.
- **Đăng ký lớp** và hủy đăng ký an toàn đồng thời (kiểm soát giới hạn `12–24 TC`, khóa dòng chống vượt sĩ số).
- Thời khóa biểu tuần cho sinh viên, giảng viên và lịch toàn trường cho Admin.
- Điểm danh, cấu hình cột điểm, nhập bảng điểm và xuất báo cáo Excel theo lớp học phần.
- Tính học phí theo tín chỉ học phí (TCHP), chia đợt nộp, thanh toán trực tuyến idempotent và phát hành biên lai PDF.

---

## 1. Chạy toàn bộ hệ thống bằng Docker Compose

Tại thư mục gốc, tạo file `.env` từ mẫu:

```powershell
Copy-Item .env.example .env
```

Cập nhật `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` và `JWT_SECRET` (tối thiểu 32 ký tự) trong `.env`, sau đó khởi chạy:

```powershell
docker compose up --build -d
```

- **Điểm vào duy nhất (Gateway + Giao diện Web)**: `http://localhost:8080`
- **Swagger UI (Tài liệu API)**: `http://localhost:8080/api/docs`

---

## 2. Chạy môi trường phát triển (Local Dev trên Windows)

### Bước 1: Khởi động MySQL và nạp dữ liệu mẫu chuẩn (`db/`)

```powershell
docker compose up -d db
docker compose cp db/schema.sql db:/tmp/schema.sql
docker compose cp db/seed/seed.sql db:/tmp/seed.sql
docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot < /tmp/schema.sql'
docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot qldt < /tmp/seed.sql'
```

> **Lưu ý**: Bộ dữ liệu chuẩn (`db/schema.sql` + `db/seed/seed.sql`) gồm 18 bảng, 1 học kỳ duy nhất (`2026.1`), 1 tài khoản Admin, 18 giảng viên (`gv001..gv018`, 0 xung đột lịch dạy), 1.000 sinh viên (`sv20210001..sv20211000`), 100 môn học, 30 phòng học và 400 lớp học phần. Dùng `alembic stamp head` sau khi nạp SQL chuẩn; không chạy chồng `alembic upgrade head` lên database vừa nạp từ `schema.sql`.

### Bước 2: Chạy Backend (`http://localhost:8000`)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic stamp head
uvicorn app.main:app --reload
```

### Bước 3: Chạy Frontend (`http://localhost:5173`)

```powershell
cd frontend
npm install
npm run dev
```

---

## 3. Tài khoản mẫu

| Vai trò | Tên đăng nhập | Mật khẩu | Mã định danh |
|---|---|---|---|
| **ADMIN** | `admin` | `admin` | Quản trị viên đào tạo |
| **LECTURER** | `gv001` .. `gv018` | `123456` | `GV001` .. `GV018` |
| **STUDENT** | `sv20210001` .. `sv20211000` | `123456` | `20210001` .. `20211000` |

---

## 4. Kiểm tra chất lượng mã nguồn (Lint, Test & Build)

```powershell
# Kiểm tra Backend (từ thư mục gốc)
python -m ruff check backend
python -m ruff format --check backend
$env:PYTHONPATH="backend"; pytest backend/tests -q

# Kiểm tra TypeScript & Build Frontend
npm --prefix frontend run build

# Kiểm thử hiệu năng & chịu tải (tùy chọn với k6)
k6 run -e SEMESTER_ID=1 -e STUDENT_USERNAME=sv20210001 -e STUDENT_PASSWORD=123456 tests/performance/registration-load.js
```

Tài liệu chi tiết về kiến trúc, nghiệp vụ, API và cơ sở dữ liệu được đặt tại [docs/00-INDEX.md](docs/00-INDEX.md).
