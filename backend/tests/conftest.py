"""
Pytest test fixtures and configuration.
"""

import os
import pytest
from pathlib import Path
import sys

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configure test environment variables before importing app
os.environ["APP_ENV"] = "testing"
os.environ["SQLITE_DB_PATH"] = "./data/test_app.db"
os.environ["CHROMA_PERSIST_DIR"] = "./data/test_chroma"
os.environ["GEMINI_API_KEY"] = ""  # Test using offline mode

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db

TEST_DATABASE_URL = "sqlite:///./data/test_app.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test tables and clean up after session."""
    Path("./data").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()  # Release Windows file lock
    test_db_path = Path("./data/test_app.db")
    if test_db_path.exists():
        try:
            test_db_path.unlink(missing_ok=True)
        except Exception:
            pass


@pytest.fixture
def db_session():
    """Provide a fresh transactional session for a test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Provide a FastAPI TestClient with overridden database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
