# UAT end-to-end (API)

`uat_api.py` là bộ UAT tự động cho 96 ca API (xác thực, phân quyền, danh mục, đăng ký lớp, thời khóa biểu, điểm danh, bảng điểm, học phí, biên lai).

## Yêu cầu

- Stack đang chạy và truy cập được API (mặc định `http://localhost:8080/api`).
- CSDL ở **trạng thái seed chuẩn**. Script thay đổi dữ liệu (đăng ký/hủy lớp, tạo/xóa môn và lớp, thay đổi sĩ số, thanh toán, phát hành hóa đơn), vì vậy cần nạp lại seed trước mỗi lần chạy.
- Python có `httpx` (khuyến nghị dùng `backend/.venv`).

## Chạy

```bash
cd /home/trang/QLDT
backend/.venv/bin/python tests/uat/uat_api.py
```

Biến môi trường:

- `QLDT_UAT_BASE_URL`: URL gốc API (mặc định `http://localhost:8080/api`).
- `QLDT_UAT_RESULTS`: đường dẫn file kết quả JSON (mặc định `tests/uat/uat_results.json`).

Script in kết quả từng ca, tổng hợp PASS/FAIL, ghi JSON và thoát `0` khi tất cả đạt.

## Sau khi chạy

Muốn chạy lại hoặc khôi phục dữ liệu kiểm thử, nạp lại schema/seed:

```bash
docker compose up -d db
docker compose cp db/schema.sql db:/tmp/schema.sql
docker compose cp db/seed/seed.sql db:/tmp/seed.sql
docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot < /tmp/schema.sql'
docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot qldt < /tmp/seed.sql'
docker compose exec backend alembic stamp head
```
