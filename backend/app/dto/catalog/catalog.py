from datetime import date

from pydantic import Field, ValidationInfo, field_validator

from app.dto.common import CamelModel, VNDateTime


# ---------- Tham chiếu nhỏ gọn (lồng trong DTO khác) ----------
class SemesterRef(CamelModel):
    id: int
    semester_code: str
    name: str


class SubjectRef(CamelModel):
    id: int
    subject_code: str
    name: str
    credits: int


class LecturerRef(CamelModel):
    id: int
    lecturer_code: str
    full_name: str


class RoomRef(CamelModel):
    id: int
    room_code: str
    building: str | None
    capacity: int


# ---------- Học kỳ ----------
class Semester(CamelModel):
    id: int
    semester_code: str
    name: str
    start_date: date
    end_date: date
    num_weeks: int


class CurrentSemester(Semester):
    current_week: int | None  # null nếu hôm nay nằm ngoài học kỳ


class Lookups(CamelModel):
    """Dữ liệu cho các ô chọn của form thêm / sửa lớp học phần."""

    subjects: list[SubjectRef]
    lecturers: list[LecturerRef]
    rooms: list[RoomRef]
    semesters: list[Semester]


# ---------- Môn học ----------
class Subject(CamelModel):
    id: int
    subject_code: str
    name: str
    credits: int
    description: str | None
    section_count: int = 0  # số lớp học phần đã mở; Service gán


class SubjectCreateRequest(CamelModel):
    subject_code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=150)
    credits: int = Field(ge=1)
    description: str | None = None


class SubjectUpdateRequest(CamelModel):
    """Không có subjectCode: mã môn học không được sửa."""

    name: str = Field(min_length=1, max_length=150)
    credits: int = Field(ge=1)
    description: str | None = None


# ---------- Lớp học phần ----------
class Section(CamelModel):
    id: int
    section_code: str
    subject: SubjectRef
    semester: SemesterRef
    lecturer: LecturerRef
    room: RoomRef
    day_of_week: int
    start_period: int
    end_period: int
    start_week: int
    end_week: int
    max_capacity: int
    current_enrollment: int
    remaining_seats: int
    full: bool
    registered_by_me: bool | None = None  # chỉ có giá trị khi role = STUDENT


class _SectionBody(CamelModel):
    """Các trường chung của yêu cầu thêm / sửa lớp học phần."""

    subject_id: int
    semester_id: int
    lecturer_id: int
    room_id: int
    day_of_week: int = Field(ge=2, le=8)
    start_period: int = Field(ge=1, le=12)
    end_period: int = Field(ge=1, le=12)
    start_week: int = Field(ge=1)
    end_week: int = Field(ge=1)
    max_capacity: int = Field(ge=1)

    # Validator gắn vào đúng trường để lỗi trả về details[].field = "endPeriod" / "endWeek"
    @field_validator("end_period")
    @classmethod
    def _end_period_after_start(cls, v: int, info: ValidationInfo) -> int:
        start = info.data.get("start_period")
        if start is not None and v < start:
            raise ValueError("Tiết kết thúc phải lớn hơn hoặc bằng tiết bắt đầu")
        return v

    @field_validator("end_week")
    @classmethod
    def _end_week_after_start(cls, v: int, info: ValidationInfo) -> int:
        start = info.data.get("start_week")
        if start is not None and v < start:
            raise ValueError("Tuần kết thúc phải lớn hơn hoặc bằng tuần bắt đầu")
        return v


class SectionCreateRequest(_SectionBody):
    section_code: str = Field(min_length=1, max_length=20)


class SectionUpdateRequest(_SectionBody):
    """Không có sectionCode. Nếu lớp đã có đăng ký, subjectId và semesterId phải giữ nguyên."""


class SectionStudent(CamelModel):
    id: int
    student_code: str
    full_name: str
    email: str | None
    cohort: str | None
    major: str | None
    registered_at: VNDateTime


class SectionStudentList(CamelModel):
    section_id: int
    section_code: str
    current_enrollment: int
    max_capacity: int
    items: list[SectionStudent]
