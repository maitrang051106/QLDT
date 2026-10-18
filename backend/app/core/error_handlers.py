"""Mọi lỗi (HTTP >= 400) đều trả cùng cấu trúc ErrorResponse:
{status, error, message, details[], path, timestamp}."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.error_codes import ERROR_SPECS, ErrorCode
from app.core.exceptions import AppError, field_error
from app.core.timeutil import now_vn

logger = logging.getLogger(__name__)

_LOC_PREFIXES = {"body", "query", "path", "header", "cookie"}


def _response(
    request: Request,
    status: int,
    error: str,
    message: str,
    details: list[dict[str, str]] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "status": status,
            "error": error,
            "message": message,
            "details": details or [],
            "path": request.url.path,
            "timestamp": now_vn().isoformat(timespec="seconds"),
        },
    )


def _field_name(loc: tuple) -> str:
    parts = [p for p in loc if isinstance(p, str) and p not in _LOC_PREFIXES]
    return parts[-1] if parts else "body"


def _validation_message(err: dict) -> str:
    kind = err.get("type", "")
    ctx = err.get("ctx") or {}
    if kind == "missing":
        return "Trường này là bắt buộc"
    if kind == "greater_than_equal":
        return f"Giá trị phải lớn hơn hoặc bằng {ctx.get('ge')}"
    if kind == "greater_than":
        return f"Giá trị phải lớn hơn {ctx.get('gt')}"
    if kind == "less_than_equal":
        return f"Giá trị phải nhỏ hơn hoặc bằng {ctx.get('le')}"
    if kind == "less_than":
        return f"Giá trị phải nhỏ hơn {ctx.get('lt')}"
    if kind == "string_too_long":
        return f"Tối đa {ctx.get('max_length')} ký tự"
    if kind == "string_too_short":
        return "Không được để trống" if ctx.get("min_length") == 1 else "Giá trị quá ngắn"
    if kind in ("int_parsing", "int_type", "int_from_float"):
        return "Phải là số nguyên"
    if kind == "json_invalid":
        return "Nội dung JSON không hợp lệ"
    if kind == "value_error":
        # validator tự viết: ValueError("Tiết kết thúc phải ...") -> "Value error, Tiết kết thúc ..."
        return str(err.get("msg", "")).removeprefix("Value error, ") or "Giá trị không hợp lệ"
    return "Giá trị không hợp lệ"


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return _response(request, exc.status, exc.code.value, exc.message, exc.details)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        field_error(_field_name(tuple(e.get("loc", ()))), _validation_message(e))
        for e in exc.errors()
    ]
    status, message = ERROR_SPECS[ErrorCode.VALIDATION_ERROR]
    return _response(request, status, ErrorCode.VALIDATION_ERROR.value, message, details)


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    mapping = {
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
    }
    code = mapping.get(exc.status_code)
    if code:
        status, message = ERROR_SPECS[code]
        return _response(request, status, code.value, message)
    # 405 và các mã HTTP khác ngoài hợp đồng: giữ nguyên mã HTTP
    return _response(request, exc.status_code, "HTTP_ERROR", "Yêu cầu không hợp lệ")


async def not_implemented_handler(request: Request, exc: NotImplementedError) -> JSONResponse:
    """Dùng tạm cho các service còn là khung (TODO)."""
    return _response(request, 501, "NOT_IMPLEMENTED", "Chức năng chưa được triển khai")


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Lỗi không xác định tại %s", request.url.path)
    status, message = ERROR_SPECS[ErrorCode.INTERNAL_ERROR]
    return _response(request, status, ErrorCode.INTERNAL_ERROR.value, message)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(NotImplementedError, not_implemented_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
