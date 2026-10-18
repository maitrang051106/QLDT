from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.entity.base import Base, BigInt


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (CheckConstraint("capacity > 0", name="capacity_positive"),)

    id: Mapped[int] = mapped_column("room_id", BigInt, primary_key=True, autoincrement=True)
    room_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    building: Mapped[str | None] = mapped_column(String(50))
    capacity: Mapped[int] = mapped_column(nullable=False)
