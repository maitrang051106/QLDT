import os

# Phải đặt TRƯỚC khi import app: cấu hình được đọc lúc import
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-secret-test-secret-test-secret-123"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.database import get_db  # noqa: E402
from app.entity import Base, Lecturer, Role, Student, User, UserStatus  # noqa: E402
from app.main import app  # noqa: E402
from app.security.password import hash_password  # noqa: E402


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()

    admin = User(
        username="admin",
        password_hash=hash_password("Admin@123"),
        full_name="Ban quản lý",
        role=Role.ADMIN,
    )
    stu = User(
        username="sv1",
        password_hash=hash_password("Sv@12345"),
        full_name="Trần Thị B",
        email="b@sis.edu.vn",
        role=Role.STUDENT,
    )
    locked = User(
        username="locked",
        password_hash=hash_password("Locked@123"),
        full_name="Bị khóa",
        role=Role.STUDENT,
        status=UserStatus.LOCKED,
    )
    gv = User(
        username="gv1",
        password_hash=hash_password("Gv@12345"),
        full_name="Nguyễn Văn A",
        role=Role.LECTURER,
    )
    session.add_all([admin, stu, locked, gv])
    session.flush()
    session.add_all(
        [
            Student(user_id=stu.id, student_code="20210001"),
            Lecturer(user_id=gv.id, lecturer_code="GV001"),
        ]
    )
    session.commit()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def login(client: TestClient, username: str, password: str) -> dict:
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['token']}"}
