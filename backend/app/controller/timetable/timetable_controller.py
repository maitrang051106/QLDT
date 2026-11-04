from fastapi import APIRouter, Body, Query

from app.core.database import DbSession
from app.dto.catalog.catalog import Section
from app.dto.common import ItemList
from app.dto.timetable.timetable import ScheduleConflict, ScheduleSlot, Timetable
from app.security.dependencies import AdminUser, LecturerUser, StudentUser
from app.service.catalog.semester_service import SemesterService
from app.service.timetable.timetable_service import TimetableService

router = APIRouter(tags=["timetable"])


@router.get(
    "/students/me/timetable", response_model=Timetable, summary="Thời khóa biểu sinh viên (UC007)"
)
def student_timetable(
    user: StudentUser,
    db: DbSession,
    semester_id: int | None = Query(None, alias="semesterId"),
    week: int | None = Query(None, ge=1),
):
    if semester_id is None:
        semester_id = SemesterService(db).get_current().id
    return TimetableService(db).student_timetable(user, semester_id, week)


@router.get(
    "/lecturers/me/timetable", response_model=Timetable, summary="Lịch dạy giảng viên (UC008)"
)
def lecturer_timetable(
    user: LecturerUser,
    db: DbSession,
    semester_id: int | None = Query(None, alias="semesterId"),
    week: int | None = Query(None, ge=1),
):
    if semester_id is None:
        semester_id = SemesterService(db).get_current().id
    return TimetableService(db).lecturer_timetable(user, semester_id, week)


@router.get(
    "/lecturers/me/sections", response_model=ItemList[Section], summary="Các lớp được phân công"
)
def lecturer_sections(
    user: LecturerUser, db: DbSession, semester_id: int | None = Query(None, alias="semesterId")
):
    if semester_id is None:
        semester_id = SemesterService(db).get_current().id
    return TimetableService(db).lecturer_sections(user, semester_id)


@router.post(
    "/timetable/check",
    summary="Kiểm tra xung đột thời khóa biểu (không ghi DB)",
)
def timetable_check(
    user: AdminUser,
    slots: list[ScheduleSlot] = Body(...),
) -> list[ScheduleConflict]:
    from app.service.timetable.conflict_engine import find_conflicts

    return [ScheduleConflict.model_validate(item) for item in find_conflicts(slots)]
