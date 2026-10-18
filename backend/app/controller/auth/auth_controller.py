from fastapi import APIRouter, Response, status

from app.core.database import DbSession
from app.dto.auth.auth import AuthResponse, LoginRequest, UserInfo
from app.security.dependencies import CurrentUser
from app.service.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse, summary="Đăng nhập (UC001)")
def login(body: LoginRequest, db: DbSession):
    return AuthService(db).login(body)


@router.get("/me", response_model=UserInfo, summary="Thông tin người dùng hiện tại")
def me(user: CurrentUser):
    return AuthService.to_user_info(user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Đăng xuất",
)
def logout(user: CurrentUser):
    # JWT stateless, không có refresh token: phía server không có gì để hủy;
    # front-end tự xóa token. Endpoint giữ lại để khớp hợp đồng API.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
