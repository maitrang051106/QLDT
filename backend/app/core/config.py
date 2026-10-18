from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "change-me-in-env"


class Settings(BaseSettings):
    """Đọc cấu hình từ biến môi trường / file .env (tên biến không phân biệt hoa thường)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Hệ thống Quản lý & Đăng ký Học phần"
    environment: str = "dev"  # dev | test | prod

    database_url: str = "mysql+pymysql://app:app@localhost:3306/course_registration?charset=utf8mb4"

    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_seconds: int = 3600  # theo quy ước API: token sống 3600 giây, không refresh

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    timezone: str = "Asia/Ho_Chi_Minh"  # +07:00


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
