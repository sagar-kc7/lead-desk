from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.auth import pwd_context
from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Lead, User

# ---------------------------------------------------------------------------
# Test database: completely separate from the real 'leaddesk' database.
# We connect to the default 'postgres' db to CREATE DATABASE, then point
# a dedicated engine at 'leaddesk_test'.
# ---------------------------------------------------------------------------

TEST_DB_URL = settings.DATABASE_URL.rsplit("/", 1)[0] + "/leaddesk_test"

_admin_engine = create_engine(
    settings.DATABASE_URL.rsplit("/", 1)[0] + "/postgres",
    isolation_level="AUTOCOMMIT",
)
with _admin_engine.connect() as conn:
    if not conn.execute(text("SELECT 1 FROM pg_database WHERE datname='leaddesk_test'")).first():
        conn.execute(text("CREATE DATABASE leaddesk_test"))
_admin_engine.dispose()

engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


# Replace the real lifespan (which runs migrations + seed against the prod DB)
# with a no-op so tests never touch 'leaddesk'.
@asynccontextmanager
async def _test_lifespan(a):
    yield


app.router.lifespan_context = _test_lifespan


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PASSWORD = "Pass@123"
_hash = pwd_context.hash(PASSWORD)


@pytest.fixture(autouse=True)
def clean_db():
    """Truncate every table and wire get_db to the test database."""
    with engine.connect() as conn:
        conn.execute(text(
            "TRUNCATE users, leads, refresh_tokens RESTART IDENTITY CASCADE"
        ))
        conn.commit()

    def _get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = TestSession()
    yield session
    session.close()


@pytest.fixture
def member(db):
    user = User(name="Test Member", email="member@test.com",
                password_hash=_hash, role="member")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin(db):
    user = User(name="Test Admin", email="admin@test.com",
                password_hash=_hash, role="admin")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
