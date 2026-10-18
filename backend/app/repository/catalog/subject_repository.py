from app.entity.catalog.subject import Subject
from app.repository.base import BaseRepository


class SubjectRepository(BaseRepository):
    # TODO: triển khai (ví dụ xem SemesterRepository / SectionRepository để theo mẫu)

    def search(self, keyword: str | None, offset: int, limit: int, sort: str | None):
        """Trả (danh sách Subject, tổng số). keyword khớp subjectCode hoặc name."""
        raise NotImplementedError

    def get_by_id(self, subject_id: int) -> Subject | None:
        return self.db.get(Subject, subject_id)

    def exists_by_code(self, subject_code: str) -> bool:
        raise NotImplementedError

    def count_sections(self, subject_id: int) -> int:
        """Số lớp học phần của môn (cho trường sectionCount và chặn xóa)."""
        raise NotImplementedError

    def add(self, subject: Subject) -> Subject:
        self.db.add(subject)
        self.db.flush()  # lấy id, chưa commit
        return subject

    def delete(self, subject: Subject) -> None:
        self.db.delete(subject)
        self.db.flush()
