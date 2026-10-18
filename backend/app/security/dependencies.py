"""Tương đương Security Filter (JwtAuthFilter + RoleChecker) trong tài liệu thiết kế.

Lớp phân quyền thứ nhất: vai trò được phép gọi endpoint (khai báo bằng kiểu tham số,
ví dụ `user: AdminUser`). Lớp thứ hai — quyền sở hữu dữ liệu (sinh viên chỉ hủy đăng ký của
mình, giảng viên chỉ xem lớp mình phụ trách) — do Service kiểm tra.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import DbSession
from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
from app.entity.auth.user import Role, User
from app.service.auth.auth_service import AuthService

# auto_error=False để tự trả ErrorResponse (UNAUTHORIZED) thay vì lỗi mặc định của FastAPI
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    """JwtAuthFilter: xác thực token, nạp người dùng, kiểm tra tài khoản ACTIVE."""
    if credentials is None:
        raise AppError(ErrorCode.UNAUTHORIZED)
    return AuthService(db).authenticate_token(credentials.credentials)


def require_roles(*roles: Role):
    """RoleChecker: chỉ cho các vai trò liệt kê đi tiếp, ngược lại 403 FORBIDDEN."""

    def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise AppError(ErrorCode.FORBIDDEN)
        return user

    return checker


# Dùng trong controller:  def endpoint(user: AdminUser, ...)
CurrentUser = Annotated[User, Depends(get_current_user)]  # mọi vai trò
AdminUser = Annotated[User, Depends(require_roles(Role.ADMIN))]
LecturerUser = Annotated[User, Depends(require_roles(Role.LECTURER))]
StudentUser = Annotated[User, Depends(require_roles(Role.STUDENT))]
AdminOrStudent = Annotated[User, Depends(require_roles(Role.ADMIN, Role.STUDENT))]
AdminOrLecturer = Annotated[User, Depends(require_roles(Role.ADMIN, Role.LECTURER))]
