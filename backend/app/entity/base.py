from sqlalchemy import BigInteger, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase

# Đặt tên ràng buộc ổn định để Alembic autogenerate / drop constraint không bị lệch tên
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# BIGINT trên MySQL; SQLite (dùng trong test) chỉ tự tăng với INTEGER PRIMARY KEY
BigInt = BigInteger().with_variant(Integer, "sqlite")


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
