from fastapi import APIRouter

from app.core.database import DbSession
from app.dto.catalog.catalog import CurrentSemester, Semester
from app.dto.common import ItemList
from app.security.dependencies import CurrentUser
from app.service.catalog.semester_service import SemesterService

router = APIRouter(prefix="/semesters", tags=["catalog"])


@router.get("", response_model=ItemList[Semester], summary="Danh sách học kỳ")
def list_semesters(_user: CurrentUser, db: DbSession):
    return SemesterService(db).list_all()


# Khai báo /current trước mọi route có path parameter (nếu sau này thêm /{id})
@router.get("/current", response_model=CurrentSemester, summary="Học kỳ hiện tại và tuần hiện tại")
def current_semester(_user: CurrentUser, db: DbSession):
    return SemesterService(db).get_current()
