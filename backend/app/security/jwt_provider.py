"""Sinh và kiểm tra JWT (NFR-002). Token chứa userId (sub), role và thời hạn."""

from dataclasses import dataclass
from datetime import timedelta

import jwt

from app.core.config import settings
from app.core.error_codes import ErrorCode
from app.core.exceptions import AppError
from app.core.timeutil import now_vn


@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    role: str


def create_token(user_id: int, role: str) -> str:
    now = now_vn()
    claims = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(seconds=settings.jwt_expire_seconds),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> TokenPayload:
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return TokenPayload(user_id=int(claims["sub"]), role=str(claims["role"]))
    except jwt.ExpiredSignatureError as exc:
        raise AppError(ErrorCode.TOKEN_EXPIRED) from exc
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise AppError(ErrorCode.UNAUTHORIZED) from exc
