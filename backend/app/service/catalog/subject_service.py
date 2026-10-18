from sqlalchemy.orm import Session

from app.dto.catalog.catalog import Subject, SubjectCreateRequest, SubjectUpdateRequest
from app.dto.common import Page, PageParams
from app.repository.catalog.subject_repository import SubjectRepository


class SubjectService:
    """UC002 – quản lý môn học (chỉ ADMIN)."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.subjects = SubjectRepository(db)

    def list(self, keyword: str | None, paging: PageParams) -> Page[Subject]:
        """TODO: tìm theo keyword (subjectCode / name), phân trang, điền sectionCount."""
        raise NotImplementedError

    def get(self, subject_id: int) -> Subject:
        """TODO: 404 NOT_FOUND nếu không có."""
        raise NotImplementedError

    def create(self, request: SubjectCreateRequest) -> Subject:
        """TODO: 409 DUPLICATE_CODE nếu trùng subjectCode; commit; trả Subject (201)."""
        raise NotImplementedError

    def update(self, subject_id: int, request: SubjectUpdateRequest) -> Subject:
        """TODO: 404 nếu không có; không đổi subjectCode; commit."""
        raise NotImplementedError

    def delete(self, subject_id: int) -> None:
        """TODO: 404 nếu không có; 409 SUBJECT_HAS_SECTIONS nếu môn đã có lớp; commit."""
        raise NotImplementedError
