import pytest
from app.database import engine, Base
import app.models  # Ensures all SQLAlchemy models are registered on Base.metadata

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
