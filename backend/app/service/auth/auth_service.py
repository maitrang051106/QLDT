from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
from app.dto.auth.auth import AuthResponse, LoginRequest, UserInfo
from app.entity.auth.user import User, UserStatus
from app.repository.auth.user_repository import UserRepository
from app.security import jwt_provider
from app.security.password import verify_password


class AuthService:
    """UC001 (đăng nhập) và UC004 (xác thực phiên)."""

    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def login(self, request: LoginRequest) -> AuthResponse:
        user = self.users.get_by_username(request.username)
        # Cùng một mã lỗi cho "sai tên" và "sai mật khẩu": không lộ tài khoản nào tồn tại
        if user is None or not verify_password(request.password, user.password_hash):
            raise AppError(ErrorCode.INVALID_CREDENTIALS)
        if user.status != UserStatus.ACTIVE:
            raise AppError(ErrorCode.ACCOUNT_LOCKED)

        return AuthResponse(
            token=jwt_provider.create_token(user.id, user.role.value),
            token_type="Bearer",
            expires_in=settings.jwt_expire_seconds,
            user=self.to_user_info(user),
        )

    def authenticate_token(self, token: str) -> User:
        """Dùng bởi Security Filter: token hợp lệ + tài khoản còn tồn tại và ACTIVE."""
        payload = jwt_provider.decode_token(token)
        user = self.users.get_by_id(payload.user_id)
        if user is None:
            raise AppError(ErrorCode.UNAUTHORIZED)
        if user.status != UserStatus.ACTIVE:
            raise AppError(ErrorCode.ACCOUNT_LOCKED)
        return user

    @staticmethod
    def to_user_info(user: User) -> UserInfo:
        return UserInfo(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            student_code=user.student.student_code if user.student else None,
            lecturer_code=user.lecturer.lecturer_code if user.lecturer else None,
        )
