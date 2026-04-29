from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from app.api import api_router
from app.core.config import get_settings
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


class CachedStaticFiles(StaticFiles):
    def __init__(self, *args, cache_seconds: int, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cache_seconds = cache_seconds

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = f"public, max-age={self.cache_seconds}"
        return response


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.api_title, version=settings.api_version, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Crediva data service is temporarily unavailable.",
                "code": "database_unavailable",
            },
        )

    app.include_router(api_router)
    static_dir = Path(__file__).parent / "static"
    app.mount(
        "/static",
        CachedStaticFiles(directory=static_dir, cache_seconds=settings.static_cache_seconds),
        name="static",
    )

    @app.get("/config", include_in_schema=False)
    def frontend_config() -> dict[str, str]:
        return {
            "apiBaseUrl": settings.frontend_api_base_url,
            "environment": settings.environment,
        }

    @app.get("/", include_in_schema=False)
    def frontend() -> FileResponse:
        response = FileResponse(static_dir / "index.html")
        response.headers["Cache-Control"] = "no-store"
        return response

    return app


app = create_app()
