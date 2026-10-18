from fastapi import APIRouter, Response, status

from app.controller.pagination import Pagination
from app.core.database import DbSession
from app.dto.catalog.catalog import Subject, SubjectCreateRequest, SubjectUpdateRequest
from app.dto.common import Page
from app.security.dependencies import AdminUser
from app.service.catalog.subject_service import SubjectService

router = APIRouter(prefix="/subjects", tags=["catalog"])


@router.get("", response_model=Page[Subject], summary="Danh sách môn học")
def list_subjects(_admin: AdminUser, db: DbSession, paging: Pagination, keyword: str | None = None):
    return SubjectService(db).list(keyword, paging)


@router.get("/{subject_id}", response_model=Subject, summary="Chi tiết môn học")
def get_subject(subject_id: int, _admin: AdminUser, db: DbSession):
    return SubjectService(db).get(subject_id)


@router.post(
    "", response_model=Subject, status_code=status.HTTP_201_CREATED, summary="Thêm môn học"
)
def create_subject(body: SubjectCreateRequest, _admin: AdminUser, db: DbSession):
    return SubjectService(db).create(body)


@router.put("/{subject_id}", response_model=Subject, summary="Sửa môn học")
def update_subject(subject_id: int, body: SubjectUpdateRequest, _admin: AdminUser, db: DbSession):
    return SubjectService(db).update(subject_id, body)


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Xóa môn học",
)
def delete_subject(subject_id: int, _admin: AdminUser, db: DbSession):
    SubjectService(db).delete(subject_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
