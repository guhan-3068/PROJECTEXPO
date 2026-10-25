from app.routers.auth import router as auth_router
from app.routers.applications import router as applications_router
from app.routers.documents import router as documents_router
from app.routers.verification import router as verification_router
from app.routers.reports import router as reports_router
from app.routers.admin import router as admin_router
from app.routers.rule_radar import router as rule_radar_router
from app.routers.timeline import router as timeline_router

__all__ = [
    "auth_router",
    "applications_router",
    "documents_router",
    "verification_router",
    "reports_router",
    "admin_router",
    "rule_radar_router",
    "timeline_router"
]
