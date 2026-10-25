from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import (
    auth_router,
    applications_router,
    documents_router,
    verification_router,
    reports_router,
    admin_router,
    rule_radar_router,
    timeline_router
)
from app.routers.applications import seed_profiles_if_empty
from app.services.rule_radar_service import rule_radar_service

def _run_db_migrations(db_engine):
    try:
        with db_engine.connect() as conn:
            inspector = inspect(conn)
            if inspector.has_table("user_applications"):
                user_app_cols = [c["name"] for c in inspector.get_columns("user_applications")]
                if "readiness_status" not in user_app_cols:
                    conn.execute(text("ALTER TABLE user_applications ADD COLUMN readiness_status VARCHAR(64) DEFAULT 'Action Required'"))
                if "state" not in user_app_cols:
                    conn.execute(text("ALTER TABLE user_applications ADD COLUMN state VARCHAR(64) DEFAULT 'Tamil Nadu'"))
                if "district" not in user_app_cols:
                    conn.execute(text("ALTER TABLE user_applications ADD COLUMN district VARCHAR(64) DEFAULT 'Chennai'"))
                if "issuing_authority" not in user_app_cols:
                    conn.execute(text("ALTER TABLE user_applications ADD COLUMN issuing_authority VARCHAR(128)"))

            if inspector.has_table("verification_results"):
                ver_cols = [c["name"] for c in inspector.get_columns("verification_results")]
                if "readiness_status" not in ver_cols:
                    conn.execute(text("ALTER TABLE verification_results ADD COLUMN readiness_status VARCHAR(64) DEFAULT 'Action Required'"))
                if "readiness_score" not in ver_cols:
                    conn.execute(text("ALTER TABLE verification_results ADD COLUMN readiness_score VARCHAR(16) DEFAULT '0%'"))
                if "prioritized_checklist" not in ver_cols:
                    conn.execute(text("ALTER TABLE verification_results ADD COLUMN prioritized_checklist TEXT DEFAULT '[]'"))
                if "action_plan" not in ver_cols:
                    conn.execute(text("ALTER TABLE verification_results ADD COLUMN action_plan TEXT DEFAULT '[]'"))
                if "confidence_summary" not in ver_cols:
                    conn.execute(text("ALTER TABLE verification_results ADD COLUMN confidence_summary TEXT DEFAULT '{}'"))
            conn.commit()
    except Exception as e:
        print(f"[DB Migration Info] {e}")

# Initialize database tables and seed default requirement profiles
Base.metadata.create_all(bind=engine)
_run_db_migrations(engine)
_db = SessionLocal()
try:
    seed_profiles_if_empty(_db)
    rule_radar_service.seed_initial_records(_db)
finally:
    _db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Document Verification System featuring OCR, Requirement Checking, Expiry Tracking, Mismatch Detection, and Forensic Anomaly Screening.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
api_v1_prefix = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(applications_router, prefix=api_v1_prefix)
app.include_router(documents_router, prefix=api_v1_prefix)
app.include_router(verification_router, prefix=api_v1_prefix)
app.include_router(reports_router, prefix=api_v1_prefix)
app.include_router(admin_router, prefix=api_v1_prefix)
app.include_router(rule_radar_router, prefix=api_v1_prefix)
app.include_router(timeline_router, prefix=api_v1_prefix)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "CONNECTED"
    }

@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to QUBIX API",
        "documentation": "/docs",
        "version": "1.0.0"
    }
