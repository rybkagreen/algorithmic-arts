import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from src.config import settings
from src.main import app as main_app
from src.models.base import Base
from src.database import get_db


@pytest.fixture(scope="session")
def db_url():
    return os.getenv("TEST_DATABASE_URL", "postgresql://algo_user:password@localhost:5432/test_algorithmic_arts")


@pytest.fixture(scope="session")
def engine(db_url):
    if not database_exists(db_url):
        create_database(db_url)
    _engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(_engine)
    yield _engine
    _engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    main_app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=main_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def test_settings():
    return settings


@pytest.fixture(scope="session")
def test_config():
    return {
        "database_url": os.getenv("TEST_DATABASE_URL", "postgresql://algo_user:password@localhost:5432/test_algorithmic_arts"),
        "redis_url": "redis://localhost:6379/1",
        "kafka_bootstrap_servers": "localhost:9092",
        "jwt_private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDQv7i3sJ6yQqK+
ZJ4uKzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMf
TnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUe
MfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHc
UeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFg
HcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZt
FgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+Qm
ZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+
QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xR
JhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8
xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYd
XqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZ
zQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYl
QJZzQYdXqL8xRJhV+QmZtFgHcUeMfTnYlQJZzQYdXqL8xRJhV+QmZtFgHcUeMf
TnYlQJZzQ== 
-----END PRIVATE KEY-----""",
    }