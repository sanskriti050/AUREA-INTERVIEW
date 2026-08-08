"""Shared test fixtures."""
import os
import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.core.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test_aurea.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    try:
        if os.path.exists("test_aurea.db"):
            os.remove("test_aurea.db")
    except PermissionError:
        pass  # Windows — file released shortly after


@pytest.fixture
def client():
    # Disable rate limiting in tests
    with patch("slowapi.middleware.SlowAPIMiddleware.__call__", new=lambda self, scope, receive, send: self.app(scope, receive, send)):
        with TestClient(app) as c:
            yield c


@pytest.fixture
def client_no_patch():
    """Client without patching — for rate limit tests."""
    return TestClient(app)


def unique_email():
    return f"user_{int(time.time() * 1000)}@test.com"


@pytest.fixture
def auth_headers(client):
    """Register a fresh user and return Bearer token headers."""
    resp = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": unique_email(),
        "password": "testpassword123"
    })
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
