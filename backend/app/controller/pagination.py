from typing import Annotated

from fastapi import Depends, Query

from app.dto.common import PageParams


def page_params(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort: str | None = Query(None, description="tenTruong,asc|desc"),
) -> PageParams:
    return PageParams(page=page, size=size, sort=sort)


Pagination = Annotated[PageParams, Depends(page_params)]
