from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controller.router import api_router
from app.core.config import DEFAULT_JWT_SECRET, settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()

    if settings.environment not in ("dev", "test") and settings.jwt_secret == DEFAULT_JWT_SECRET:
        raise RuntimeError("Phải đặt JWT_SECRET khi chạy ngoài môi trường dev/test")

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        # Để tài liệu nằm dưới /api để API Gateway chỉ cần định tuyến một tiền tố
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,  # dùng header Authorization, không dùng cookie
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["infra"], include_in_schema=False)
    def health() -> dict[str, str]:
        """Cho Docker HEALTHCHECK / API Gateway / CI; không cần xác thực."""
        return {"status": "ok"}

    return app


app = create_app()
