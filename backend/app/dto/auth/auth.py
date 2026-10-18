from pydantic import ConfigDict, Field

from app.dto.common import CamelModel
from app.entity.auth.user import Role


class LoginRequest(CamelModel):
    model_config = ConfigDict(
        str_strip_whitespace=False
    )  # không được cắt khoảng trắng của mật khẩu

    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=100)


class UserInfo(CamelModel):
    id: int
    username: str
    full_name: str
    email: str | None
    role: Role
    student_code: str | None  # chỉ role = STUDENT
    lecturer_code: str | None  # chỉ role = LECTURER


class AuthResponse(CamelModel):
    token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserInfo
