"""Gom mọi controller dưới tiền tố /api (không đánh số phiên bản)."""

from fastapi import APIRouter

from app.controller.auth import auth_controller
from app.controller.catalog import section_controller, semester_controller, subject_controller
from app.controller.registration import registration_controller
from app.controller.timetable import timetable_controller
from app.dto.common import ErrorResponse

# Tài liệu hóa cấu trúc lỗi chung trong OpenAPI / Swagger
_ERRORS = {
    400: {"model": ErrorResponse},
    401: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
}

api_router = APIRouter(prefix="/api", responses=_ERRORS)
for _module in (
    auth_controller,
    semester_controller,
    subject_controller,
    section_controller,
    registration_controller,
    timetable_controller,
):
    api_router.include_router(_module.router)
