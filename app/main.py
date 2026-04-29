from fastapi import FastAPI

from app.api import api_router
from app.core.config import get_settings
from app.db.session import Base, engine


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.api_title, version=settings.api_version)
    app.include_router(api_router)
    return app


app = create_app()


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
