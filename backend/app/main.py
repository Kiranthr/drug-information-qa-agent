"""
FastAPI Main Application Entrypoint for Drug Information Q&A Agent.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db, get_db
from app.db.vector_store import vector_store
from app.models.sql_models import Medicine, Document
from app.models.schemas import HealthCheckResponse

from app.api.v1.endpoints_chat import router as chat_router
from app.api.v1.endpoints_medicines import router as medicines_router
from app.api.v1.endpoints_documents import router as documents_router
from app.api.v1.endpoints_safety import router as safety_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: initialize database tables and directories on startup."""
    logger.info("Starting up Drug Information Q&A Agent backend...")
    settings.ensure_directories()
    init_db()
    logger.info("Application startup complete.")
    yield
    logger.info("Shutting down backend...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Evidence-grounded Drug Information Q&A Agent using RAG and Google Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
API_PREFIX = "/api/v1"
app.include_router(chat_router, prefix=API_PREFIX)
app.include_router(medicines_router, prefix=API_PREFIX)
app.include_router(documents_router, prefix=API_PREFIX)
app.include_router(safety_router, prefix=API_PREFIX)


@app.get("/api/v1/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint returning system status, database statistics,
    vector index count, and active providers.
    """
    try:
        med_count = db.query(Medicine).count()
        doc_count = db.query(Document).count()
        chunk_count = vector_store.count_chunks()
        db_ok = True
    except Exception as e:
        logger.error(f"Health check database query error: {e}")
        med_count = 0
        doc_count = 0
        chunk_count = 0
        db_ok = False

    return HealthCheckResponse(
        status="ok" if db_ok else "degraded",
        app_name=settings.APP_NAME,
        app_env=settings.APP_ENV,
        database_connected=db_ok,
        total_medicines=med_count,
        total_documents=doc_count,
        vector_chunks_indexed=chunk_count,
        llm_provider=f"Google Gemini ({settings.GEMINI_MODEL})" if settings.GEMINI_API_KEY else "Offline Grounded Fallback",
        embedding_provider=settings.EMBEDDING_PROVIDER
    )


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Drug Information Q&A Agent API",
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
        "version": "1.0.0"
    }
