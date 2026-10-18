"""Quy ước: CSDL lưu DATETIME theo giờ Việt Nam (không kèm múi giờ);
JSON luôn trả ISO 8601 kèm +07:00."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.core.config import settings

VN_TZ = ZoneInfo(settings.timezone)


def now_vn() -> datetime:
    """Thời điểm hiện tại, có múi giờ."""
    return datetime.now(VN_TZ)


def now_vn_naive() -> datetime:
    """Dùng làm default cho cột DATETIME."""
    return now_vn().replace(tzinfo=None)


def today_vn() -> date:
    return now_vn().date()


def to_vn(value: datetime) -> datetime:
    """Gắn / đổi về múi giờ +07:00 (giá trị từ CSDL là naive giờ VN)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=VN_TZ)
    return value.astimezone(VN_TZ)
