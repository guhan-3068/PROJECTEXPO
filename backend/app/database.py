from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Engine configuration with SQLite thread handling and WAL mode for Windows stability
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 30.0}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

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

_run_db_migrations(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
