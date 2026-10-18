# API Gateway (Nginx)

Điểm vào duy nhất của hệ thống; client chỉ biết một địa chỉ, không biết backend/front-end nằm ở đâu.

| Đường dẫn | Đi tới | Ghi chú |
|---|---|---|
| `/api/*` | Backend (FastAPI) | gồm `/api/docs`, `/api/openapi.json` |
| `/health` | chính gateway | liveness |
| `/health/backend` | backend `/health` | kiểm tra gateway → backend thông |
| `/*` | Front-end | cùng origin với API → **không cần CORS** khi đi qua gateway |

## Gateway làm gì (và không làm gì)

**Làm:** định tuyến; giới hạn tốc độ theo IP (`/api/auth/login` chặt hơn); giới hạn kích thước body (1 MB);
gắn `X-Request-Id` (cũng chuyển xuống backend) và `X-Forwarded-*`; header bảo mật; nén gzip;
timeout; **biến lỗi do gateway sinh ra (429, 413, 502, 503, 504) thành JSON đúng cấu trúc `ErrorResponse`**;
không retry request ghi (tránh đăng ký trùng); lỗi của backend đi nguyên vẹn.

**Không làm:** xác thực JWT và phân quyền. Theo tài liệu thiết kế, việc này thuộc Security Filter ở backend
(kiểm tra ở mọi request, kể cả khi ai đó gọi thẳng backend), nên gateway không nhân đôi logic.

## Chạy

```bash
# Cả hệ thống (từ thư mục gốc repo)
docker compose up --build
python gateway/smoke_test.py            # kiểm tra nhanh, mặc định http://localhost:8080

# Dev: API chạy bằng uvicorn trong VS Code, gateway trong Docker
docker compose up -d db gateway         # đặt BACKEND_URL=http://host.docker.internal:8000
```

Cấu hình qua biến môi trường (có mặc định trong `Dockerfile`): `BACKEND_URL`, `FRONTEND_URL`,
`API_RATE` (30r/s), `LOGIN_RATE` (30r/m), `DNS_RESOLVER` (127.0.0.11, DNS nội bộ của Docker).

## Cần thống nhất với nhóm front-end

Quy ước API hiện chưa có hai mã lỗi mới do gateway trả:
`TOO_MANY_REQUESTS` (429, kèm `Retry-After`) và `PAYLOAD_TOO_LARGE` (413).
Với 502/503/504 gateway dùng `error = INTERNAL_ERROR` nhưng `status` là mã HTTP thật.

## Khi lên HTTPS (triển khai thật)

Gắn chứng chỉ vào gateway (thêm `listen 443 ssl;`, `ssl_certificate*`), chuyển `80` → `443`,
bỏ comment `Strict-Transport-Security`. Cân nhắc chặn `/api/docs` ở môi trường production.
