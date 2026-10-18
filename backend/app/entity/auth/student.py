from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.entity.base import Base, BigInt

if TYPE_CHECKING:
    from app.entity.auth.user import User


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column("student_id", BigInt, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInt, ForeignKey("users.user_id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    student_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    cohort: Mapped[str | None] = mapped_column(String(10))
    major: Mapped[str | None] = mapped_column(String(100))

    user: Mapped["User"] = relationship(back_populates="student")

    @property
    def full_name(self) -> str:
        return self.user.full_name

    @property
    def email(self) -> str | None:
        return self.user.email
