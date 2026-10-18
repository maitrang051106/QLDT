import datetime as dt

from app.dto.common import CamelModel


class TimetableItem(CamelModel):
    section_id: int
    section_code: str
    subject_code: str
    subject_name: str
    day_of_week: int
    date: dt.date  # ngày học cụ thể trong tuần được chọn
    start_period: int
    end_period: int
    room_code: str
    lecturer_name: str
    start_week: int
    end_week: int


class Timetable(CamelModel):
    semester_id: int
    week: int
    week_start_date: dt.date  # Thứ hai
    week_end_date: dt.date  # Chủ nhật
    items: list[TimetableItem]  # sắp theo dayOfWeek rồi startPeriod
