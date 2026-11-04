# Mục lục Tài liệu Dự án (Document Index)

Đọc đúng tài liệu cần thiết cho tác vụ đang thực hiện để tiết kiệm ngữ cảnh (context window):

| Tác vụ đang thực hiện | Tài liệu cần đọc |
|---|---|
| Tổng quan dự án & quy tắc làm việc chung | [../CLAUDE.md](../CLAUDE.md), [../AGENTS.md](../AGENTS.md) |
| Đặc tả yêu cầu (UC001–UC010, Học phí) & Quy tắc nghiệp vụ | [srs-and-rules.md](srs-and-rules.md) |
| Quy ước API FE–BE, Mã lỗi, Ánh xạ trường & Thiết kế CSDL (18 bảng) | [api-and-database.md](api-and-database.md), `../contracts/openapi.yaml`, `../contracts/api-types.ts` |
| Phát triển & Kiểm thử Backend | [../backend/CLAUDE.md](../backend/CLAUDE.md), [api-and-database.md](api-and-database.md) |
| Phát triển & Tích hợp Frontend | [../frontend/CLAUDE.md](../frontend/CLAUDE.md), [api-and-database.md](api-and-database.md) |
| Truy vết tính năng, Tiến độ & Kịch bản kiểm thử | [traceability-and-testing.md](traceability-and-testing.md) |
| Cài đặt môi trường, Docker, Gateway & CI/CD | [../README.md](../README.md), [../gateway/README.md](../gateway/README.md), `../docker-compose.yml` |

## Thứ tự ưu tiên của nguồn chuẩn

1. `contracts/openapi.yaml` và `contracts/api-types.ts` là hợp đồng kỹ thuật đọc bằng máy có độ ưu tiên cao nhất giữa Frontend và Backend.
2. `db/schema.sql` và `db/seed/seed.sql` là nguồn chuẩn duy nhất cho cấu trúc bảng (18 bảng) và dữ liệu mẫu của MySQL.
3. Ba tài liệu [srs-and-rules.md](srs-and-rules.md), [api-and-database.md](api-and-database.md) và [traceability-and-testing.md](traceability-and-testing.md) tổng hợp toàn bộ quy tắc nghiệp vụ, quy ước API/CSDL và ma trận truy vết của hệ thống.
