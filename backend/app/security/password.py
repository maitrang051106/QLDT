"""Băm / so khớp mật khẩu bằng Bcrypt, có salt (NFR-001)."""

import bcrypt


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:  # hash hỏng, hoặc mật khẩu dài quá 72 byte (giới hạn của bcrypt)
        return False
