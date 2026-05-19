"""Pytest configuration.

Sets up an isolated SQLite test database BEFORE importing any backend modules
so that `backend.database.engine` is bound to the test DB, not `./tetris.db`.
A fresh schema is rebuilt before every test for full isolation.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Make the project root (parent of `backend/`) importable.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Configure env BEFORE importing backend modules so the engine binds to test DB.
_TEST_DB = Path(tempfile.gettempdir()) / "tetris_pytest.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ["SECRET_KEY"] = "test-secret-for-pytest"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.database import Base, engine  # noqa: E402
from backend.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_db():
    """Drop and recreate all tables before each test for full isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    """FastAPI TestClient bound to the app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def make_user(client):
    """Register + login a user; return the access token."""
    def _make(email: str, password: str, nickname: str) -> str:
        r = client.post("/auth/register", json={
            "email": email, "password": password, "nickname": nickname,
        })
        assert r.status_code == 201, r.text
        r = client.post("/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        return r.json()["access_token"]
    return _make


def auth(token: str) -> dict[str, str]:
    """Build an Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}
