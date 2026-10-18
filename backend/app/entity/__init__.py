from app.entity.auth.lecturer import Lecturer
from app.entity.auth.student import Student
from app.entity.auth.user import Role, User, UserStatus
from app.entity.base import Base
from app.entity.catalog.course_section import CourseSection
from app.entity.catalog.room import Room
from app.entity.catalog.semester import Semester
from app.entity.catalog.subject import Subject
from app.entity.registration.registration import Registration

__all__ = [
    "Base",
    "CourseSection",
    "Lecturer",
    "Registration",
    "Role",
    "Room",
    "Semester",
    "Student",
    "Subject",
    "User",
    "UserStatus",
]
