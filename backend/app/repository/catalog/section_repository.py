from sqlalchemy import or_, select, update
from sqlalchemy.engine import CursorResult

from app.entity.catalog.course_section import CourseSection
from app.repository.base import BaseRepository


class SectionRepository(BaseRepository):
    def get_by_id(self, section_id: int) -> CourseSection | None:
        return self.db.get(CourseSection, section_id)

    def search(
        self,
        semester_id: int,
        subject_id: int | None,
        keyword: str | None,
        offset: int,
        limit: int,
        sort: str | None,
    ):
        """Trả (danh sách CourseSection, tổng số). TODO: dùng joinedload để tránh N+1."""
        raise NotImplementedError

    def list_by_lecturer(self, lecturer_id: int, semester_id: int) -> list[CourseSection]:
        raise NotImplementedError

    def exists_by_code(self, section_code: str) -> bool:
        raise NotImplementedError

    def add(self, section: CourseSection) -> CourseSection:
        self.db.add(section)
        self.db.flush()
        return section

    def delete(self, section: CourseSection) -> None:
        self.db.delete(section)
        self.db.flush()

    # ---- Truy vấn xung đột lịch (mục 3.3): cùng học kỳ, cùng thứ, tiết giao nhau,
    # ---- tuần giao nhau, và trùng phòng HOẶC trùng giảng viên.
    def find_room_or_lecturer_conflicts(
        self,
        *,
        semester_id: int,
        room_id: int,
        lecturer_id: int,
        day_of_week: int,
        start_period: int,
        end_period: int,
        start_week: int,
        end_week: int,
        exclude_section_id: int | None = None,  # khi sửa lớp: loại trừ chính lớp đó
    ) -> list[CourseSection]:
        stmt = select(CourseSection).where(
            CourseSection.semester_id == semester_id,
            CourseSection.day_of_week == day_of_week,
            CourseSection.start_period <= end_period,
            CourseSection.end_period >= start_period,
            CourseSection.start_week <= end_week,
            CourseSection.end_week >= start_week,
            or_(CourseSection.room_id == room_id, CourseSection.lecturer_id == lecturer_id),
        )
        if exclude_section_id is not None:
            stmt = stmt.where(CourseSection.id != exclude_section_id)
        return list(self.db.scalars(stmt).all())

    # ---- Cập nhật sĩ số nguyên tử (mục 3.3) ----
    def increment_enrollment_if_available(self, section_id: int) -> bool:
        """UPDATE ... SET current_enrollment = current_enrollment + 1
        WHERE section_id = :id AND current_enrollment < max_capacity.
        True nếu tăng được; False (0 dòng bị ảnh hưởng) nghĩa là lớp đã đầy -> CLASS_FULL."""
        result: CursorResult = self.db.execute(  # type: ignore[assignment]
            update(CourseSection)
            .where(
                CourseSection.id == section_id,
                CourseSection.current_enrollment < CourseSection.max_capacity,
            )
            .values(current_enrollment=CourseSection.current_enrollment + 1)
        )
        return result.rowcount == 1

    def decrement_enrollment(self, section_id: int) -> None:
        self.db.execute(
            update(CourseSection)
            .where(CourseSection.id == section_id, CourseSection.current_enrollment > 0)
            .values(current_enrollment=CourseSection.current_enrollment - 1)
        )
