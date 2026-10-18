from sqlalchemy.orm import Session


class BaseRepository:
    """Repository chỉ truy cập CSDL, không chứa quy tắc nghiệp vụ và không commit
    (Service quyết định ranh giới giao dịch)."""

    def __init__(self, db: Session) -> None:
        self.db = db
