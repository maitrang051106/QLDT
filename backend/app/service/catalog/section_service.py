from sqlalchemy.orm import Session

from app.dto.catalog.catalog import (
    Lookups,
    Section,
    SectionCreateRequest,
    SectionStudentList,
    SectionUpdateRequest,
)
from app.dto.common import Page, PageParams
from app.entity.auth.user import User
from app.repository.catalog.lookup_repository import LookupRepository
from app.repository.catalog.section_repository import SectionRepository
from app.repository.registration.registration_repository import RegistrationRepository


class SectionService:
    """UC002 (CRUD lớp học phần), UC003 và UC009 (danh sách sinh viên của lớp)."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.sections = SectionRepository(db)
        self.registrations = RegistrationRepository(db)
        self.lookups = LookupRepository(db)

    def list(
        self,
        user: User,
        semester_id: int,
        subject_id: int | None,
        keyword: str | None,
        paging: PageParams,
    ) -> Page[Section]:
        """TODO: ADMIN và STUDENT. Điền registeredByMe khi role = STUDENT, còn lại null."""
        raise NotImplementedError

    def get(self, section_id: int) -> Section:
        """TODO: 404 NOT_FOUND."""
        raise NotImplementedError

    def get_lookups(self) -> Lookups:
        """TODO: subjects, lecturers, rooms, semesters cho form."""
        raise NotImplementedError

    def create(self, request: SectionCreateRequest) -> Section:
        """TODO: 404 nếu subject/semester/lecturer/room không tồn tại; 409 DUPLICATE_CODE;
        endWeek <= numWeeks; maxCapacity <= sức chứa phòng (400 VALIDATION_ERROR);
        409 SCHEDULE_CONFLICT (details[] nêu mã lớp xung đột, dùng
        SectionRepository.find_room_or_lecturer_conflicts); currentEnrollment = 0."""
        raise NotImplementedError

    def update(self, section_id: int, request: SectionUpdateRequest) -> Section:
        """TODO: 404; 409 CAPACITY_BELOW_ENROLLMENT nếu maxCapacity < currentEnrollment;
        409 SECTION_HAS_REGISTRATIONS nếu đã có đăng ký mà đổi subjectId/semesterId;
        kiểm tra xung đột lịch có exclude_section_id."""
        raise NotImplementedError

    def delete(self, section_id: int) -> None:
        """TODO: 404; 409 SECTION_HAS_REGISTRATIONS nếu đã có sinh viên đăng ký."""
        raise NotImplementedError

    def list_students(self, user: User, section_id: int) -> SectionStudentList:
        """TODO: 404 nếu lớp không tồn tại. ADMIN xem mọi lớp; LECTURER chỉ lớp mình phụ trách
        (section.lecturer.user_id == user.id), ngược lại 403 FORBIDDEN."""
        raise NotImplementedError
