# QLDT Project Harness

## Tổng quan dự án

Hệ thống Quản lý & Đăng ký Học phần trực tuyến (môn IT3180 – Nhóm 20). Kho mã nguồn được chia thành các phần: hợp đồng API (`contracts/`), Backend (`backend/`), Frontend (`frontend/`), Cơ sở dữ liệu (`db/`), Tài liệu (`docs/`), Cổng định tuyến (`gateway/`), CI/CD (`.github/workflows/`) và Kiểm thử hiệu năng (`tests/performance/`).

## Nguồn chuẩn (Source of Truth)

- Đọc [docs/00-INDEX.md](docs/00-INDEX.md) để tra cứu đúng tài liệu cần thiết cho từng tác vụ.
- Quy ước API FE–BE trong [docs/api-and-database.md](docs/api-and-database.md) có độ ưu tiên cao nhất.
- `contracts/openapi.yaml` và `contracts/api-types.ts` là hợp đồng API chính thức và kiểu TypeScript dùng chung cho toàn dự án.
- Lược đồ SQL (17 bảng) và dữ liệu mẫu nằm tại `db/schema.sql` và `db/seed/seed.sql` (đã bỏ cơ chế chia đợt nộp `TUITION_INSTALLMENTS`).
- Backend sử dụng FastAPI + SQLAlchemy 2 + Alembic trong `backend/app/`; các bản migration giữ nguyên tên bảng viết hoa (`UPPER_SNAKE_CASE`) như trong `db/schema.sql`.
- Xem [backend/CLAUDE.md](backend/CLAUDE.md) cho quy tắc Backend: hệ thống bao phủ UC001–UC010, kiểm tra xung đột thời khóa biểu và thu học phí/biên lai điện tử; chỉ vận hành trên **1 học kỳ đang mở đăng ký duy nhất (`2026.1`)** với giới hạn tín chỉ `12–24 TC`. Không áp dụng điều kiện học phần tiên quyết, học phần song hành, đổi lớp nguyên tử hay miễn giảm học phí.
- `docker-compose.yml` khởi chạy toàn bộ stack (`db`, `backend`, `frontend`, `gateway`). Cổng MySQL host được map là `3308:3306` để tránh xung đột WinNAT/Windows services trên cổng 3306. Khởi tạo DB nạp qua lệnh `source /tmp/...` của MySQL client bên trong container.
- `.github/workflows/ci-cd.yml` tự động kiểm tra lint, test, migration, build Frontend và smoke test qua Gateway.

## Quy tắc làm việc chung

- Code Frontend đặt tại `frontend/`; code Backend đặt tại `backend/app/`, kiểm thử logic & API tại `backend/tests/`, và kịch bản đo tải K6 tại `tests/performance/`.
- Giữ đồng bộ tuyệt đối tên trường JSON `camelCase`, enum `UPPER_SNAKE_CASE`, mã lỗi nghiệp vụ và tiền tố `/api`. Thống nhất thuật ngữ **"Đăng ký lớp"** trên cả giao diện và tài liệu API.
- Backend chịu trách nhiệm kiểm tra điều kiện đăng ký, giới hạn tín chỉ, trùng lịch và sĩ số lớp. Frontend luôn gọi lại API (`refetch`) sau mỗi thao tác ghi, tuyệt đối không tự cộng/trừ sĩ số ở phía client.
- Giảng viên chỉ được điểm danh, nhập điểm và xuất báo cáo Excel cho các lớp mình phụ trách; `ADMIN` cấu hình cột điểm và xem danh sách sinh viên.
- Lỗi HTTP `401` xóa phiên đăng nhập và đưa về trang `/login`. Lỗi HTTP `403` chỉ hiển thị thông báo từ chối quyền truy cập, không đăng xuất.
- Không bao giờ để lộ mật khẩu, chuỗi băm mật khẩu (`password_hash`), token, câu lệnh SQL hoặc stack trace ra giao diện hay log.
