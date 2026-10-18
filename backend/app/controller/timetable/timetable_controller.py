from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.dto.catalog.catalog import Section
from app.dto.common import ItemList
from app.dto.timetable.timetable import Timetable
from app.security.dependencies import LecturerUser, StudentUser
from app.service.timetable.timetable_service import TimetableService

router = APIRouter(tags=["timetable"])


@router.get(
    "/students/me/timetable", response_model=Timetable, summary="Thời khóa biểu sinh viên (UC007)"
)
def student_timetable(
    user: StudentUser,
    db: DbSession,
    semester_id: int = Query(alias="semesterId"),
    week: int | None = Query(None, ge=1),
):
    return TimetableService(db).student_timetable(user, semester_id, week)


@router.get(
    "/lecturers/me/timetable", response_model=Timetable, summary="Lịch dạy giảng viên (UC008)"
)
def lecturer_timetable(
    user: LecturerUser,
    db: DbSession,
    semester_id: int = Query(alias="semesterId"),
    week: int | None = Query(None, ge=1),
):
    return TimetableService(db).lecturer_timetable(user, semester_id, week)


@router.get(
    "/lecturers/me/sections", response_model=ItemList[Section], summary="Các lớp được phân công"
)
def lecturer_sections(
    user: LecturerUser, db: DbSession, semester_id: int = Query(alias="semesterId")
):
    return TimetableService(db).lecturer_sections(user, semester_id)
