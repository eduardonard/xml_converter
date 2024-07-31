from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv
import os

import pytest

load_dotenv()

client = TestClient(app)


@pytest.fixture
def setup_env_vars(monkeypatch):
    """
    Fixture to set up environment variables for tests.
    """
    monkeypatch.setenv("USERNAME", os.environ.get("USERNAME"))
    monkeypatch.setenv("PASSWORD", os.environ.get("PASSWORD"))


@pytest.mark.unit
def test_authenticate_valid_credentials(setup_env_vars):
    response = client.get(
        "/export", auth=(os.environ.get("USERNAME"), os.environ.get("PASSWORD"))
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_authenticate_invalid_username(setup_env_vars):
    response = client.get(
        "/export", auth=("invaliduser", os.environ.get("PASSWORD"))
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


@pytest.mark.unit
def test_authenticate_invalid_password(setup_env_vars):
    response = client.get("/export", auth=(os.environ.get("USERNAME"), "wrongpass"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


@pytest.mark.unit
def test_authenticate_missing_credentials(setup_env_vars):
    response = client.get("/export")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Basic"
