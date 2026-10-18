"""Nạp dữ liệu mẫu cho môi trường dev (tài khoản được nạp sẵn vào CSDL, chưa có API tạo tài khoản).

    python -m scripts.seed

Chạy lại nhiều lần an toàn (bỏ qua bản ghi đã có). KHÔNG dùng mật khẩu này ở môi trường thật.
"""

from datetime import date

from sqlalchemy import select

from app.core.database import SessionLocal
from app.entity import Lecturer, Role, Room, Semester, Student, Subject, User
from app.security.password import hash_password


def _get_or_create_user(db, username, password, full_name, email, role):
    user = db.scalars(select(User).where(User.username == username)).first()
    if user is None:
        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            email=email,
            role=role,
        )
        db.add(user)
        db.flush()
    return user


def main() -> None:
    with SessionLocal() as db:
        _get_or_create_user(db, "admin", "Admin@123", "Ban quản lý", "admin@sis.edu.vn", Role.ADMIN)

        gv = _get_or_create_user(
            db, "gv001", "Gv@12345", "Nguyễn Văn A", "a.nv@sis.edu.vn", Role.LECTURER
        )
        if gv.lecturer is None:
            db.add(Lecturer(user_id=gv.id, lecturer_code="GV001", department="Khoa học máy tính"))

        sv = _get_or_create_user(
            db, "sv20260001", "Sv@12345", "Trần Thị B", "b.tt@sis.edu.vn", Role.STUDENT
        )
        if sv.student is None:
            db.add(
                Student(
                    user_id=sv.id, student_code="20210001", cohort="K66", major="Khoa học máy tính"
                )
            )

        if not db.scalars(select(Semester).where(Semester.semester_code == "2026.1")).first():
            db.add(
                Semester(
                    semester_code="2026.1",
                    name="Học kỳ 1 năm học 2026-2027",
                    start_date=date(2026, 9, 7),
                    end_date=date(2026, 12, 20),
                    num_weeks=15,
                )
            )
        if not db.scalars(select(Room).where(Room.room_code == "D9-301")).first():
            db.add(Room(room_code="D9-301", building="D9", capacity=60))
        if not db.scalars(select(Subject).where(Subject.subject_code == "IT3180")).first():
            db.add(Subject(subject_code="IT3180", name="Nhập môn Công nghệ phần mềm", credits=3))

        db.commit()
    print("Đã nạp dữ liệu mẫu: admin / gv001 / sv20260001")


if __name__ == "__main__":
    main()
