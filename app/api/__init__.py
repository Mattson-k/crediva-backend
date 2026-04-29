from fastapi import APIRouter

from app.api import health, licenses, monitors, webhooks

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(licenses.router)
api_router.include_router(monitors.router)
api_router.include_router(webhooks.router)
