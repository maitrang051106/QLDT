from sqlalchemy import select

from app.entity.auth.student import Student
from app.entity.auth.user import User
from app.repository.base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalars(select(User).where(User.username == username)).first()


class StudentRepository(BaseRepository):
    def get_by_user_id(self, user_id: int) -> Student | None:
        return self.db.scalars(select(Student).where(Student.user_id == user_id)).first()
