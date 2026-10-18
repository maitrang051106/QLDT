from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.entity.base import Base, BigInt

if TYPE_CHECKING:
    from app.entity.auth.user import User


class Lecturer(Base):
    __tablename__ = "lecturers"

    id: Mapped[int] = mapped_column("lecturer_id", BigInt, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInt, ForeignKey("users.user_id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    lecturer_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    department: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="lecturer")

    @property
    def full_name(self) -> str:
        return self.user.full_name
