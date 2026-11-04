from app.dto.catalog.catalog import Section
from app.dto.common import CamelModel, VNDateTime


class RegisterRequest(CamelModel):
    section_id: int


class Registration(CamelModel):
    id: int
    registered_at: VNDateTime
    section: Section
