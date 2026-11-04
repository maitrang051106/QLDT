# Quy tắc Kiến trúc & Giao diện Frontend

- **Công nghệ**: React 19, TypeScript, Vite, Ant Design 5, React Router 7, Axios, TanStack Query 5.
- **Cấu trúc thư mục**:
  - Các phân hệ nghiệp vụ đặt tại `src/modules/{auth,catalog,registration,timetable,tuition}`.
  - Khung ứng dụng và định tuyến đặt tại `src/app/`; thành phần dùng chung (API client, kiểu dữ liệu, giao diện, tiện ích) đặt tại `src/shared/`.
- **Kết nối API**:
  - `baseURL` mặc định là `/api`. Mọi đường dẫn gọi từ `api` client đều viết tương đối so với `/api`.
  - Không tự suy đoán tên trường dữ liệu; luôn sử dụng kiểu từ `src/shared/api/api-types.ts` (đồng bộ 100% với `contracts/api-types.ts` và `contracts/openapi.yaml`).
- **Quy tắc hiển thị & Nghiệp vụ**:
  - **Một học kỳ duy nhất (`2026.1`)**: Các màn hình danh mục lớp, đăng ký lớp, thời khóa biểu và học phí tự động gắn với học kỳ hiện tại và hiển thị bằng nhãn (`Tag`) cố định, không dùng ô chọn chuyển đổi nhiều học kỳ.
  - **Thuật ngữ thống nhất**: Sử dụng **"Đăng ký lớp"** cho chức năng đăng ký lớp học phần (`/app/sections`).
  - **Danh sách sinh viên lớp (UC003 & UC009)**: Màn hình `SectionRosterPage` (`/app/sections/:sectionId/students`) phục vụ cả Giảng viên phụ trách (kèm tab Điểm danh, Bảng điểm, Xuất Excel) và Admin (truy cập qua nút **"Danh sách SV"** tại `AdminCatalogPage`).
  - **Học phí & Biên lai**:
    - Sinh viên (`/app/tuition` – `StudentTuitionPage`): Xem tổng học phí, chi tiết môn học theo TCHP, tiến độ các đợt nộp, thanh toán trực tuyến và tải PDF biên lai.
    - Quản trị viên (`/app/tuition/manage` – `AdminTuitionPage`): Xem thống kê thu học phí toàn kỳ, phát hành/cập nhật hóa đơn hàng loạt, quản lý bảng đơn giá và các đợt nộp.
- **Xử lý lỗi & Trạng thái**:
  - Rẽ nhánh xử lý lỗi dựa trên mã `error` trong `ErrorResponse`, không dựa vào chuỗi `message`. Gắn chi tiết lỗi `VALIDATION_ERROR` (`details[]`) vào đúng trường trên biểu mẫu.
  - Tuyệt đối không tự tính toán hoặc cập nhật lạc quan (`optimistic update`) sĩ số lớp ở phía client; luôn gọi `invalidateQueries` / `refetch` sau khi thao tác thành công.
  - Lỗi `401` xóa token và chuyển hướng về `/login`; lỗi `403` giữ nguyên phiên đăng nhập và hiển thị thông báo không đủ quyền.
