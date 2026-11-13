# Nhật ký lỗi UAT (Bug Log)

## 1. Thông tin chung

| Hạng mục | Giá trị |
|---|---|
| Ngày kiểm thử | 2026-11-13 |
| Môi trường | Hệ thống QLDT với bộ dữ liệu seed chuẩn |
| Phạm vi | UC001–UC010 (xác thực, danh mục, đăng ký lớp, thời khóa biểu, điểm danh, bảng điểm, học phí, biên lai) |
| Kết quả | **0 lỗi** trong phạm vi UAT |

Báo cáo chi tiết các ca kiểm thử xem tại [uat-report.md](uat-report.md).

## 2. Danh sách lỗi

Không có lỗi nào được xác nhận.

| ID | Mức độ | Mô tả | Trạng thái |
|---|---|---|---|
| — | — | Không phát hiện lỗi chức năng trong 112 ca UAT | — |

## 3. Quan sát trong quá trình kiểm thử (không phải lỗi sản phẩm)

Các mục dưới đây được ghi lại để tránh nhầm lẫn khi đọc kết quả, không phải khuyết điểm của hệ thống.

### OBS-01: JWT không bị thu hồi phía máy chủ sau đăng xuất

- **Hiện tượng:** Token cũ vẫn gọi được API sau khi `POST /auth/logout` trả `204`.
- **Nguyên nhân:** Thiết kế xác thực stateless bằng JWT; đăng xuất chỉ xóa token phía client (`sessionStorage`).
- **Đánh giá:** Phù hợp thiết kế hiện tại; token có thời hạn cố định. Nếu cần thu hồi tức thời, phải bổ sung cơ chế denylist/refresh token (ngoài phạm vi UAT).
- **Kết luận:** Không phải lỗi trong phạm vi yêu cầu.

### OBS-02: Cột “Trạng thái chỗ” hiển thị dạng “còn lại / tối đa”

- **Hiện tượng:** Lớp còn trống hiển thị `40 / 40`, lớp đầy hiển thị `Đã đầy` hoặc `0 / 1`.
- **Đánh giá:** Cách hiển thị nhất quán với nhãn “Trạng thái chỗ” (số chỗ còn lại trên tổng sức chứa). Không gây sai lệch nghiệp vụ.
- **Kết luận:** Không phải lỗi; có thể cải thiện nhãn thành “còn 40/40” trong tương lai nếu muốn rõ hơn.

## 4. Thang mức độ lỗi (áp dụng cho các đợt sau)

| Mức độ | Định nghĩa |
|---|---|
| Critical | Mất dữ liệu, lộ dữ liệu nhạy cảm, phá vỡ phân quyền, không thể đăng nhập/thanh toán |
| High | Sai lệch nghiệp vụ trọng yếu (học phí, điểm, đăng ký), chặn luồng chính |
| Medium | Chức năng chạy được nhưng sai điều kiện biên hoặc thông báo lỗi |
| Low | Lỗi giao diện, nhãn, định dạng, trải nghiệm người dùng |

## 5. Mẫu ghi nhận lỗi

```
ID: BUG-xxx
Mức độ: Critical / High / Medium / Low
Vai trò: ADMIN / LECTURER / STUDENT / Công khai
Màn hình hoặc endpoint:
Bước tái hiện:
  1.
  2.
  3.
Kỳ vọng:
Thực tế:
Dữ liệu/ảnh chụp/log kèm theo:
Ảnh hưởng:
Đề xuất hướng sửa:
Trạng thái: Mới / Đang xử lý / Đã sửa / Đóng
```
