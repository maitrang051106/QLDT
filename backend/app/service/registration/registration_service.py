from sqlalchemy.orm import Session

from app.dto.common import ItemList
from app.dto.registration.registration import RegisterRequest, Registration
from app.entity.auth.user import User
from app.repository.auth.user_repository import StudentRepository
from app.repository.catalog.section_repository import SectionRepository
from app.repository.registration.registration_repository import RegistrationRepository


class RegistrationService:
    """UC005 (đăng ký) và UC006 (hủy). Mỗi thao tác ghi là MỘT giao dịch: db.commit() ở cuối,
    lỗi nghiệp vụ -> ném AppError (get_db sẽ rollback)."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.students = StudentRepository(db)
        self.sections = SectionRepository(db)
        self.registrations = RegistrationRepository(db)

    def register(self, user: User, request: RegisterRequest) -> Registration:
        """TODO theo thứ tự (mục 5.8):
        1. 404 NOT_FOUND nếu lớp không tồn tại; studentId lấy từ token (StudentRepository).
        2. 409 ALREADY_REGISTERED          <- RegistrationRepository.exists
        3. 409 SAME_SUBJECT_REGISTERED     <- find_same_subject
        4. 409 STUDENT_SCHEDULE_CONFLICT   <- find_schedule_conflicts (details[] nêu mã lớp)
        5. SectionRepository.increment_enrollment_if_available: False -> 409 CLASS_FULL
        6. RegistrationRepository.add; commit; trả Registration (201) với sĩ số đã tăng
           (db.refresh(section) trước khi dựng DTO vì UPDATE đi thẳng xuống CSDL)."""
        raise NotImplementedError

    def cancel(self, user: User, registration_id: int) -> None:
        """TODO (mục 5.9): 404 nếu không tồn tại; 403 FORBIDDEN nếu thuộc sinh viên khác;
        delete + decrement_enrollment trong cùng giao dịch; commit."""
        raise NotImplementedError

    def list_mine(self, user: User, semester_id: int) -> ItemList[Registration]:
        """TODO: các lớp đã đăng ký của sinh viên trong học kỳ (registeredByMe = true)."""
        raise NotImplementedError
