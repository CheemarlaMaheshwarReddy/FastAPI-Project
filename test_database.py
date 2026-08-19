import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base, User
from utils import pwd_context


TEST_DATABASE_URL = os.getenv(
     "TEST_DATABASE_URL",
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


def test_database_1(setup_database):
    print("Running test 1")
    assert len(Base.metadata.tables) > 0


def test_database_2(setup_database):
    print("Running test 2")
    assert len(Base.metadata.tables) > 0


def test_test_user(test_user):
    print("Test user:", test_user.email)

    assert test_user.email == "test@example.com"
    assert pwd_context.verify("password123", test_user.password)
