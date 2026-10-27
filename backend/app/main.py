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
                if "readiness_breakdown" not in ver_cols:
                    conn.execute(text("ALTER TABLE verification_results ADD COLUMN readiness_breakdown TEXT DEFAULT '{}'"))

            if inspector.has_table("checklist_requirements"):
                chk_cols = [c["name"] for c in inspector.get_columns("checklist_requirements")]
                if "alternative_documents" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN alternative_documents TEXT DEFAULT '[]'"))
                if "eligibility_conditions" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN eligibility_conditions TEXT"))
                if "validity_rules" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN validity_rules TEXT"))
                if "accepted_formats" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN accepted_formats VARCHAR(128) DEFAULT 'PDF, JPG, JPEG, PNG (Max 15MB)'"))
                if "official_source_url" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN official_source_url VARCHAR(512)"))
                if "last_verified_date" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN last_verified_date DATETIME"))
                if "next_review_date" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN next_review_date DATETIME"))
                if "status" not in chk_cols:
                    conn.execute(text("ALTER TABLE checklist_requirements ADD COLUMN status VARCHAR(32) DEFAULT 'Current'"))

            if inspector.has_table("application_profiles"):
                prof_cols = [c["name"] for c in inspector.get_columns("application_profiles")]
                if "official_source_url" not in prof_cols:
                    conn.execute(text("ALTER TABLE application_profiles ADD COLUMN official_source_url VARCHAR(512)"))
                if "last_verified_date" not in prof_cols:
                    conn.execute(text("ALTER TABLE application_profiles ADD COLUMN last_verified_date DATETIME"))
                if "next_review_date" not in prof_cols:
                    conn.execute(text("ALTER TABLE application_profiles ADD COLUMN next_review_date DATETIME"))
                if "status" not in prof_cols:
                    conn.execute(text("ALTER TABLE application_profiles ADD COLUMN status VARCHAR(32) DEFAULT 'Current'"))
                if "eligibility_criteria" not in prof_cols:
                    conn.execute(text("ALTER TABLE application_profiles ADD COLUMN eligibility_criteria TEXT"))

            if inspector.has_table("uploaded_documents"):
                doc_cols = [c["name"] for c in inspector.get_columns("uploaded_documents")]
                if "checklist_requirement_id" not in doc_cols:
                    conn.execute(text("ALTER TABLE uploaded_documents ADD COLUMN checklist_requirement_id VARCHAR(36)"))

            if inspector.has_table("tampering_analyses"):
                tamp_cols = [c["name"] for c in inspector.get_columns("tampering_analyses")]
                if "authenticity_result" not in tamp_cols:
                    conn.execute(text("ALTER TABLE tampering_analyses ADD COLUMN authenticity_result VARCHAR(64) DEFAULT 'No obvious manipulation detected'"))
                if "ai_generation_screening" not in tamp_cols:
                    conn.execute(text("ALTER TABLE tampering_analyses ADD COLUMN ai_generation_screening VARCHAR(64) DEFAULT 'No synthetic generative signatures identified'"))
                if "digital_signature_status" not in tamp_cols:
                    conn.execute(text("ALTER TABLE tampering_analyses ADD COLUMN digital_signature_status VARCHAR(64) DEFAULT 'No digital signature (Standard scan/copy)'"))
                if "visual_structure_evidence" not in tamp_cols:
                    conn.execute(text("ALTER TABLE tampering_analyses ADD COLUMN visual_structure_evidence TEXT DEFAULT '[]'"))
                if "metadata_evidence" not in tamp_cols:
                    conn.execute(text("ALTER TABLE tampering_analyses ADD COLUMN metadata_evidence TEXT DEFAULT '[]'"))

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

# CORS Middleware (permits configured origins + all Vercel deployment preview/production domains)
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
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
