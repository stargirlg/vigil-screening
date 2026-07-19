import pytest
import uuid
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.auth.password import hash_password

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

TEST_CUSTOMER_ID = uuid.UUID("e506847c-ea3b-4630-b229-fd5c85f10535")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    # Create admin user
    existing = db.query(User).filter(
        User.email == "admin@vigil.com"
    ).first()

    if not existing:
        admin = User(
            email="admin@vigil.com",
            full_name="Test Admin",
            hashed_password=hash_password("Admin@123!"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)

    # Create test customer
    existing_customer = db.query(Customer).filter(
        Customer.id == TEST_CUSTOMER_ID
    ).first()

    if not existing_customer:
        customer = Customer(
            id=TEST_CUSTOMER_ID,
            full_name="Test Customer",
            dob=date(1990, 1, 1),
            pan="ABCDE1234F",
            aadhaar="123456789012",
            nationality="India",
            occupation="Engineer",
            source="TEST",
        )
        db.add(customer)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_token(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@vigil.com",
            "password": "Admin@123!"
        }
    )

    assert response.status_code == 200, f"Login failed: {response.json()}"

    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }