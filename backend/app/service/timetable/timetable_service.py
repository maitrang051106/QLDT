from sqlalchemy.orm import Session

from app.dto.catalog.catalog import Section
from app.dto.common import ItemList
from app.dto.timetable.timetable import Timetable
from app.entity.auth.user import User
from app.repository.catalog.section_repository import SectionRepository
from app.repository.catalog.semester_repository import SemesterRepository
from app.repository.registration.registration_repository import RegistrationRepository


class TimetableService:
    """UC007 (thời khóa biểu sinh viên), UC008 (lịch dạy giảng viên)."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.semesters = SemesterRepository(db)
        self.sections = SectionRepository(db)
        self.registrations = RegistrationRepository(db)

    def student_timetable(self, user: User, semester_id: int, week: int | None) -> Timetable:
        """TODO: 404 nếu học kỳ không tồn tại; week mặc định = tuần hiện tại (week_of() trong
        SemesterService); 400 INVALID_WEEK nếu week ngoài 1..numWeeks.
        weekStartDate = startDate + (week-1)*7 ngày (Thứ hai); weekEndDate = +6 ngày.
        Lấy lớp đã đăng ký có startWeek <= week <= endWeek; date = weekStartDate + (dayOfWeek-2);
        sắp theo dayOfWeek rồi startPeriod."""
        raise NotImplementedError

    def lecturer_timetable(self, user: User, semester_id: int, week: int | None) -> Timetable:
        """TODO: như trên nhưng lấy các lớp được phân công cho giảng viên đang đăng nhập."""
        raise NotImplementedError

    def lecturer_sections(self, user: User, semester_id: int) -> ItemList[Section]:
        """TODO: các lớp được phân công trong học kỳ (UC008, UC009)."""
        raise NotImplementedError
