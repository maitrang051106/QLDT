from datetime import date

from sqlalchemy import CheckConstraint, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.entity.base import Base, BigInt


class Semester(Base):
    __tablename__ = "semesters"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="date_range"),
        CheckConstraint("num_weeks > 0", name="num_weeks_positive"),
    )

    id: Mapped[int] = mapped_column("semester_id", BigInt, primary_key=True, autoincrement=True)
    semester_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)  # mốc tính tuần 1
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    num_weeks: Mapped[int] = mapped_column(nullable=False)
