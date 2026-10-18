from sqlalchemy import select

from app.entity.catalog.semester import Semester
from app.repository.base import BaseRepository


class SemesterRepository(BaseRepository):
    """Dùng chung cho module catalog (GET /semesters) và timetable (tính tuần)."""

    def list_all(self) -> list[Semester]:
        return list(self.db.scalars(select(Semester).order_by(Semester.start_date.desc())).all())

    def get_by_id(self, semester_id: int) -> Semester | None:
        return self.db.get(Semester, semester_id)
