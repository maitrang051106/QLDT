"""Bộ mã lỗi nghiệp vụ — khớp mục 5 của tài liệu "Quy ước API và JSON".
Front-end rẽ nhánh theo mã (trường `error`), không theo `message`."""

from enum import Enum


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_WEEK = "INVALID_WEEK"
    UNAUTHORIZED = "UNAUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE_CODE = "DUPLICATE_CODE"
    SCHEDULE_CONFLICT = "SCHEDULE_CONFLICT"
    SUBJECT_HAS_SECTIONS = "SUBJECT_HAS_SECTIONS"
    SECTION_HAS_REGISTRATIONS = "SECTION_HAS_REGISTRATIONS"
    CAPACITY_BELOW_ENROLLMENT = "CAPACITY_BELOW_ENROLLMENT"
    CLASS_FULL = "CLASS_FULL"
    ALREADY_REGISTERED = "ALREADY_REGISTERED"
    SAME_SUBJECT_REGISTERED = "SAME_SUBJECT_REGISTERED"
    STUDENT_SCHEDULE_CONFLICT = "STUDENT_SCHEDULE_CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# mã lỗi -> (HTTP status, thông báo mặc định tiếng Việt)
ERROR_SPECS: dict[ErrorCode, tuple[int, str]] = {
    ErrorCode.VALIDATION_ERROR: (400, "Dữ liệu không hợp lệ"),
    ErrorCode.INVALID_WEEK: (400, "Tuần không thuộc học kỳ đã chọn"),
    ErrorCode.UNAUTHORIZED: (401, "Bạn chưa đăng nhập"),
    ErrorCode.TOKEN_EXPIRED: (401, "Phiên đăng nhập đã hết hạn"),
    ErrorCode.INVALID_CREDENTIALS: (401, "Tên đăng nhập hoặc mật khẩu chưa đúng"),
    ErrorCode.ACCOUNT_LOCKED: (403, "Tài khoản đã bị khóa"),
    ErrorCode.FORBIDDEN: (403, "Bạn không có quyền thực hiện thao tác này"),
    ErrorCode.NOT_FOUND: (404, "Không tìm thấy dữ liệu"),
    ErrorCode.DUPLICATE_CODE: (409, "Mã đã tồn tại"),
    ErrorCode.SCHEDULE_CONFLICT: (409, "Trùng phòng học hoặc giảng viên"),
    ErrorCode.SUBJECT_HAS_SECTIONS: (409, "Môn học đã có lớp học phần, không thể xóa"),
    ErrorCode.SECTION_HAS_REGISTRATIONS: (409, "Lớp học phần đã có sinh viên đăng ký"),
    ErrorCode.CAPACITY_BELOW_ENROLLMENT: (
        409,
        "Sĩ số tối đa không được nhỏ hơn số sinh viên đã đăng ký",
    ),
    ErrorCode.CLASS_FULL: (409, "Lớp học phần đã đủ sĩ số"),
    ErrorCode.ALREADY_REGISTERED: (409, "Bạn đã đăng ký lớp học phần này"),
    ErrorCode.SAME_SUBJECT_REGISTERED: (409, "Bạn đã đăng ký môn học này ở lớp khác"),
    ErrorCode.STUDENT_SCHEDULE_CONFLICT: (409, "Lớp trùng lịch học với lớp bạn đã đăng ký"),
    ErrorCode.INTERNAL_ERROR: (500, "Hệ thống đang gặp lỗi, vui lòng thử lại sau"),
}
