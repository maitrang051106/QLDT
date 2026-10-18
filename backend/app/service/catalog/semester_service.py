from datetime import date

from sqlalchemy.orm import Session

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
from app.core.timeutil import today_vn
from app.dto.catalog.catalog import CurrentSemester, Semester
from app.dto.common import ItemList
from app.entity.catalog.semester import Semester as SemesterEntity
from app.repository.catalog.semester_repository import SemesterRepository


def week_of(semester: SemesterEntity, day: date) -> int | None:
    """Tuần thứ mấy của học kỳ (tuần 1 bắt đầu từ startDate); None nếu ngoài học kỳ."""
    if day < semester.start_date or day > semester.end_date:
        return None
    week = (day - semester.start_date).days // 7 + 1
    return week if week <= semester.num_weeks else None


class SemesterService:
    def __init__(self, db: Session) -> None:
        self.semesters = SemesterRepository(db)

    def list_all(self) -> ItemList[Semester]:
        items = [Semester.model_validate(s) for s in self.semesters.list_all()]
        return ItemList[Semester](items=items)

    def get_current(self) -> CurrentSemester:
        """Học kỳ chứa hôm nay; nếu không có thì lấy học kỳ gần nhất đã bắt đầu
        (currentWeek = null). Chưa có học kỳ nào -> 404."""
        today = today_vn()
        all_semesters = self.semesters.list_all()  # đã sắp theo start_date giảm dần
        if not all_semesters:
            raise AppError(ErrorCode.NOT_FOUND)

        chosen = next((s for s in all_semesters if s.start_date <= today <= s.end_date), None)
        if chosen is None:
            chosen = next((s for s in all_semesters if s.start_date <= today), all_semesters[-1])

        base = Semester.model_validate(chosen).model_dump()
        return CurrentSemester(**base, current_week=week_of(chosen, today))
