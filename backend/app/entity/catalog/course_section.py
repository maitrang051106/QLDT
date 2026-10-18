from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.entity.base import Base, BigInt

if TYPE_CHECKING:
    from app.entity.auth.lecturer import Lecturer
    from app.entity.catalog.room import Room
    from app.entity.catalog.semester import Semester
    from app.entity.catalog.subject import Subject


class CourseSection(Base):
    """Lớp học phần được mở trong học kỳ."""

    __tablename__ = "course_sections"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 2 AND 8", name="day_of_week_range"),
        CheckConstraint("start_period BETWEEN 1 AND 12", name="start_period_range"),
        CheckConstraint("end_period >= start_period AND end_period <= 12", name="end_period_range"),
        CheckConstraint("start_week >= 1", name="start_week_min"),
        CheckConstraint("end_week >= start_week", name="end_week_range"),
        CheckConstraint("max_capacity > 0", name="max_capacity_positive"),
        # lớp bảo vệ cuối cùng chống vượt sĩ số (mục 3.3)
        CheckConstraint(
            "current_enrollment >= 0 AND current_enrollment <= max_capacity",
            name="enrollment_range",
        ),
        Index("ix_course_sections_semester_subject", "semester_id", "subject_id"),
        Index("ix_course_sections_lecturer_semester", "lecturer_id", "semester_id"),
    )

    id: Mapped[int] = mapped_column("section_id", BigInt, primary_key=True, autoincrement=True)
    section_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    subject_id: Mapped[int] = mapped_column(
        BigInt, ForeignKey("subjects.subject_id", ondelete="RESTRICT"), nullable=False
    )
    semester_id: Mapped[int] = mapped_column(
        BigInt, ForeignKey("semesters.semester_id", ondelete="RESTRICT"), nullable=False
    )
    lecturer_id: Mapped[int] = mapped_column(
        BigInt, ForeignKey("lecturers.lecturer_id", ondelete="RESTRICT"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        BigInt, ForeignKey("rooms.room_id", ondelete="RESTRICT"), nullable=False
    )

    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 2..8 (8 = Chủ nhật)
    start_period: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_period: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    max_capacity: Mapped[int] = mapped_column(nullable=False)
    current_enrollment: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")

    # Các quan hệ tải khi cần (lazy mặc định). Repository dùng joinedload/selectinload
    # tường minh cho các truy vấn danh sách để tránh N+1 (NFR-005: < 2 giây).
    subject: Mapped["Subject"] = relationship()
    semester: Mapped["Semester"] = relationship()
    lecturer: Mapped["Lecturer"] = relationship()
    room: Mapped["Room"] = relationship()

    @property
    def remaining_seats(self) -> int:
        return self.max_capacity - self.current_enrollment

    @property
    def full(self) -> bool:
        return self.current_enrollment >= self.max_capacity
