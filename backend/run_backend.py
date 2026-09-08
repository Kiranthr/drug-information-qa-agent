"""
Backend startup script.
Run from repository root: python backend/run_backend.py
"""

import sys
from pathlib import Path

# Add backend directory to sys.path so 'app' package imports work cleanly
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} on http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"Interactive API Docs available at http://{settings.API_HOST}:{settings.API_PORT}/docs")
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
