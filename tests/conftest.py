import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_token(client):
    response = client.post("/auth/login", json={
        "email": "admin@vigil.com",
        "password": "Admin@123!"
    })
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}