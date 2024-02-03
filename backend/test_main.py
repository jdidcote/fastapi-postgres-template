import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from database import Base
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health():
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == "Ok"


def test_empty_authors(test_db):
    response = client.get("/authors/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_author(test_db):
    response = client.post("/authors/", json={
        "name": "string"
    })

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "string"
    }