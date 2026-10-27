import sys
import os
from pathlib import Path

# Add backend directory to sys.path so app.* modules resolve correctly
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Serverless environment adjustments for Vercel execution
if os.environ.get("VERCEL"):
    # /tmp is the only writable directory in Vercel Serverless Functions
    os.environ.setdefault("STORAGE_ROOT", "/tmp/storage")
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/docverify.db")

from app.main import app

# Vercel WSGI/ASGI entry point
# Exports the FastAPI application instance
