import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import create_access_token
from main import app
from model import Base, User, get_db
from utils import pwd_context


TEST_DATABASE_URL = (
    "postgresql://fastapi_user:FastAPI123@localhost:5433/fastapi_test_db"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user(setup_database):
    db = TestingSessionLocal()

    hashed_password = pwd_context.hash("password123")

    user = User(
        email="test@example.com",
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    db.delete(user)
    db.commit()
    db.close()

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_products(setup_database):
    response = client.get("/products/")

    print("Status code:", response.status_code)
    print("Response:", response.json())

    assert response.status_code == 200


def test_login(test_user):
    response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "Wrong Passord",
        },
    )

    print("Invalid login status:", response.status_code)
    print("Invalid login response:", response.json())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_nonexistent_user():
    response = client.post(
        "/users/login",
        data={
            "username": "doesnotexist@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_success(test_user):
    response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    print("Login status:", response.status_code)
    print("Login response:", response.json())

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_products_me_without_token():
    response = client.get("/products/me")

    print("No token status:", response.status_code)
    print("No token response:", response.json())

    assert response.status_code == 401

def test_products_me_with_token(test_user):
    login_response = client.post(
        "/users/login",
        data={
            "username": test_user.email,
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/products/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    print("Products me status:", response.status_code)
    print("Products me response:", response.json())

    assert response.status_code == 200

def test_products_me_invalid_token():
    response = client.get(
        "/products/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    print("Invalid token status:", response.status_code)
    print("Invalid token response:", response.json())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_products_me_token_without_user_id():
    token = create_access_token({})

    response = client.get(
        "/products/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    print("Missing user_id status:", response.status_code)
    print("Missing user_id response:", response.json())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_products_me_user_not_found():
    token = create_access_token({
        "user_id": 999999
    })

    response = client.get(
        "/products/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
