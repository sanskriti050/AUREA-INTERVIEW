"""Auth endpoint tests."""
import time
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.core.config import Settings


def unique_email():
    return f"user_{int(time.time() * 1000)}@test.com"


class TestRegister:

    def test_production_rejects_sqlite(self):
        with pytest.raises(ValidationError, match="PostgreSQL"):
            Settings(APP_ENV="production", DATABASE_URL="sqlite:///./app.db", SECRET_KEY="a" * 64)

    def test_production_rejects_example_secret(self):
        with pytest.raises(ValidationError, match="unique SECRET_KEY"):
            Settings(APP_ENV="production", DATABASE_URL="postgresql://user:pass@db/aurea", SECRET_KEY="CHANGE_THIS_GENERATE_WITH_SECRETS_TOKEN_HEX_32")
    def test_register_success(self, client: TestClient):
        resp = client.post("/api/auth/register", json={
            "name": "Alice Smith",
            "email": unique_email(),
            "password": "securepass123"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client: TestClient):
        email = unique_email()
        client.post("/api/auth/register", json={"name": "Alice Test", "email": email, "password": "pass1234"})
        resp = client.post("/api/auth/register", json={"name": "Alice Test", "email": email, "password": "pass1234"})
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"].lower()

    def test_register_short_password(self, client: TestClient):
        resp = client.post("/api/auth/register", json={
            "name": "Bob", "email": unique_email(), "password": "short"
        })
        assert resp.status_code == 422

    def test_register_short_name(self, client: TestClient):
        resp = client.post("/api/auth/register", json={
            "name": "A", "email": unique_email(), "password": "longpassword"
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, client: TestClient):
        resp = client.post("/api/auth/register", json={
            "name": "Bob", "email": "not-an-email", "password": "longpassword"
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient):
        email = unique_email()
        client.post("/api/auth/register", json={"name": "Carol", "email": email, "password": "mypassword1"})
        resp = client.post("/api/auth/login", json={"email": email, "password": "mypassword1"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client: TestClient):
        email = unique_email()
        client.post("/api/auth/register", json={"name": "Dave", "email": email, "password": "correctpass"})
        resp = client.post("/api/auth/login", json={"email": email, "password": "wrongpass"})
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        resp = client.post("/api/auth/login", json={"email": "nobody@nowhere.com", "password": "anything"})
        assert resp.status_code == 401


class TestMe:
    def test_get_me_authenticated(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "email" in data
        assert "name" in data

    def test_get_me_unauthenticated(self, client: TestClient):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client: TestClient):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401
