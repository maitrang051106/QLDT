from app.core.error_codes import ERROR_SPECS, ErrorCode


def field_error(field: str, message: str) -> dict[str, str]:
    """Một phần tử của details[] (tên trường camelCase, message tiếng Việt)."""
    return {"field": field, "message": message}


class AppError(Exception):
    """Lỗi nghiệp vụ. Service ném AppError, error_handlers đổi thành ErrorResponse.

    Ví dụ:
        raise AppError(ErrorCode.CLASS_FULL)
        raise AppError(ErrorCode.SCHEDULE_CONFLICT,
                       details=[field_error("roomId", "Phòng D9-301 đã có lớp 150002 cùng thời gian")])
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str | None = None,
        details: list[dict[str, str]] | None = None,
    ) -> None:
        status, default_message = ERROR_SPECS[code]
        self.code = code
        self.status = status
        self.message = message or default_message
        self.details = details or []
        super().__init__(self.message)
