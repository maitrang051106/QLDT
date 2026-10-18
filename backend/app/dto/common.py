"""Thành phần dùng chung của mọi DTO theo quy ước JSON:
camelCase, danh sách luôn nằm trong `items`, ngày giờ có +07:00."""

from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Annotated, Generic, TypeVar

from pydantic import AfterValidator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.core.timeutil import to_vn


class CamelModel(BaseModel):
    """Lớp gốc của mọi DTO.
    - Code Python viết snake_case, JSON vào/ra là camelCase (alias_generator).
    - populate_by_name: trong code vẫn khởi tạo được bằng tên snake_case.
    - from_attributes: dựng DTO trực tiếp từ Entity (Subject.model_validate(entity))."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
    )


# Ngày giờ: ISO 8601 kèm +07:00 (giá trị từ CSDL là naive giờ VN)
VNDateTime = Annotated[datetime, AfterValidator(to_vn)]

T = TypeVar("T")


class FieldError(CamelModel):
    field: str
    message: str


class ErrorResponse(CamelModel):
    status: int
    error: str
    message: str
    details: list[FieldError] = []
    path: str
    timestamp: str


class ItemList(CamelModel, Generic[T]):
    """Danh sách không phân trang: { "items": [...] }."""

    items: list[T]


@dataclass
class PageParams:
    page: int = 1
    size: int = 20
    sort: str | None = None  # "tenTruong,asc|desc"

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class Page(CamelModel, Generic[T]):
    """Danh sách có phân trang (môn học, lớp học phần)."""

    items: list[T]
    page: int
    size: int
    total_items: int
    total_pages: int

    @classmethod
    def of(cls, items: list, params: PageParams, total: int) -> "Page":
        pages = ceil(total / params.size) if total else 0
        return cls(
            items=items, page=params.page, size=params.size, total_items=total, total_pages=pages
        )
