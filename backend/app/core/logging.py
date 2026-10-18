import logging

from app.core.config import settings


def setup_logging() -> None:
    level = logging.DEBUG if settings.environment == "dev" else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
