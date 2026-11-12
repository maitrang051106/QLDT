# Quy tắc dành cho AI Agent

Đọc [CLAUDE.md](CLAUDE.md) để nắm cấu trúc dự án và nguồn sự thật (source of truth). Khi làm việc với Frontend, đọc thêm [frontend/CLAUDE.md](frontend/CLAUDE.md); khi làm việc với Backend, đọc thêm [backend/CLAUDE.md](backend/CLAUDE.md).

## Thỏa thuận làm việc

- Luôn hỏi lại người dùng nếu có bất kỳ yêu cầu nào ngầm định, mơ hồ hoặc chưa rõ ràng trước khi thực hiện.
- Một thành viên không tự ý sửa code thuộc phạm vi của thành viên khác khi chưa được phép. Nếu phát hiện lỗi ngoài phạm vi nhiệm vụ hiện tại, hãy báo cáo rõ tên file, nguyên nhân tái hiện, mức độ ảnh hưởng và hướng sửa đề xuất rồi chờ phê duyệt.
- Nếu vô tình làm thay đổi code ngoài phạm vi nhiệm vụ, phải hoàn tác (revert) và báo cáo lại thay vì để nguyên.

## Quy tắc Nghiệp vụ & Kỹ thuật trọng yếu

- **CSDL 17 bảng**: Tuyệt đối không tái sinh bảng `TUITION_INSTALLMENTS` hay các trường liên quan đến đợt nộp học phí. Mô hình học phí là thanh toán **một lần duy nhất** cho toàn bộ số nợ còn lại.
- **Hiển thị Giảng viên**: Luôn duy trì bộ lọc `lecturerKeyword` trong API danh mục lớp học phần (`/api/sections`) và hiển thị đầy đủ họ tên giảng viên trên mọi giao diện sinh viên (bảng lớp, giỏ đăng ký, TKB dự kiến, lớp đã đăng ký, TKB chính thức).
- **Thao tác Docker & Môi trường Windows**:
  - Cổng MySQL trên máy host là `3308:3306` (tránh xung đột cổng 3306 với WinNAT hoặc dịch vụ MySQL của Windows).
  - Trên PowerShell, tránh sử dụng toán tử bash như `&&` (thay bằng dấu chấm phẩy `;`) hoặc dấu chuyển hướng `<` khi chạy lệnh Docker (sử dụng `-e "source /tmp/..."` của MySQL client).
  - Chạy migration Alembic trực tiếp bên trong container backend (`docker compose exec backend alembic stamp head` hoặc `upgrade head`) để đảm bảo đúng biến môi trường mạng nội bộ Docker.

