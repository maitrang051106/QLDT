from sqlalchemy import select

from app.entity.auth.lecturer import Lecturer
from app.entity.catalog.room import Room
from app.entity.catalog.subject import Subject
from app.repository.base import BaseRepository


class LookupRepository(BaseRepository):
    """Danh sách cho ô chọn (dropdown) của form lớp học phần."""

    def list_subjects(self) -> list[Subject]:
        return list(self.db.scalars(select(Subject).order_by(Subject.subject_code)).all())

    def list_lecturers(self) -> list[Lecturer]:
        return list(self.db.scalars(select(Lecturer).order_by(Lecturer.lecturer_code)).all())

    def list_rooms(self) -> list[Room]:
        return list(self.db.scalars(select(Room).order_by(Room.room_code)).all())
