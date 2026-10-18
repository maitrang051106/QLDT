from sqlalchemy import select

from app.entity.catalog.course_section import CourseSection
from app.entity.registration.registration import Registration
from app.repository.base import BaseRepository


class RegistrationRepository(BaseRepository):
    def get_by_id(self, registration_id: int) -> Registration | None:
        return self.db.get(Registration, registration_id)

    def add(self, registration: Registration) -> Registration:
        self.db.add(registration)
        self.db.flush()
        return registration

    def delete(self, registration: Registration) -> None:
        self.db.delete(registration)
        self.db.flush()

    def exists(self, student_id: int, section_id: int) -> bool:
        stmt = select(Registration.id).where(
            Registration.student_id == student_id, Registration.section_id == section_id
        )
        return self.db.scalars(stmt).first() is not None

    def find_same_subject(
        self, student_id: int, subject_id: int, semester_id: int
    ) -> Registration | None:
        """Sinh viên đã đăng ký lớp khác của cùng môn trong học kỳ chưa?"""
        stmt = (
            select(Registration)
            .join(CourseSection, Registration.section_id == CourseSection.id)
            .where(
                Registration.student_id == student_id,
                CourseSection.subject_id == subject_id,
                CourseSection.semester_id == semester_id,
            )
        )
        return self.db.scalars(stmt).first()

    def find_schedule_conflicts(
        self, student_id: int, section: CourseSection
    ) -> list[CourseSection]:
        """Các lớp sinh viên đã đăng ký mà trùng thứ + giao tiết + giao tuần với `section`."""
        stmt = (
            select(CourseSection)
            .join(Registration, Registration.section_id == CourseSection.id)
            .where(
                Registration.student_id == student_id,
                CourseSection.semester_id == section.semester_id,
                CourseSection.id != section.id,
                CourseSection.day_of_week == section.day_of_week,
                CourseSection.start_period <= section.end_period,
                CourseSection.end_period >= section.start_period,
                CourseSection.start_week <= section.end_week,
                CourseSection.end_week >= section.start_week,
            )
        )
        return list(self.db.scalars(stmt).all())

    def list_by_student(self, student_id: int, semester_id: int) -> list[Registration]:
        raise NotImplementedError  # TODO: join CourseSection, lọc học kỳ, joinedload

    def list_students_of_section(self, section_id: int) -> list[Registration]:
        raise NotImplementedError  # TODO: kèm Student + User để lấy họ tên, email
