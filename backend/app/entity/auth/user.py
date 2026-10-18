import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.entity.base import Base, BigInt

if TYPE_CHECKING:
    from app.entity.auth.lecturer import Lecturer
    from app.entity.auth.student import Student


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    LECTURER = "LECTURER"
    STUDENT = "STUDENT"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column("user_id", BigInt, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # không bao giờ vào JSON
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), unique=True)
    role: Mapped[Role] = mapped_column(SAEnum(Role, name="user_role"), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, name="user_status"), nullable=False, default=UserStatus.ACTIVE
    )

    # joined: mỗi request đều cần studentCode / lecturerCode cho UserInfo
    student: Mapped[Optional["Student"]] = relationship(
        back_populates="user", uselist=False, lazy="joined"
    )
    lecturer: Mapped[Optional["Lecturer"]] = relationship(
        back_populates="user", uselist=False, lazy="joined"
    )
