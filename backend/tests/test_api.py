from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_and_login():
    payload = {
        "email": "admin@example.com",
        "password": "StrongPass123",
        "full_name": "Admin User",
        "role": "admin",
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200, res.text
    assert "access_token" in res.json()

    login = client.post("/api/v1/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200, login.text
    assert "access_token" in login.json()


def test_waste_category_and_report_flow():
    admin_payload = {
        "email": "admin2@example.com",
        "password": "StrongPass123",
        "full_name": "Admin User 2",
        "role": "admin",
    }
    admin_res = client.post("/api/v1/auth/register", json=admin_payload)
    admin_token = admin_res.json()["access_token"]

    category_res = client.post(
        "/api/v1/waste-categories/",
        json={
            "name": "Plastic",
            "category_type": "recyclable",
            "description": "Plastic waste and packaging",
            "is_recyclable": True,
            "is_organic": False,
            "is_hazardous": False,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert category_res.status_code == 200, category_res.text
    category_id = category_res.json()["id"]

    citizen_payload = {
        "email": "citizen@example.com",
        "password": "StrongPass123",
        "full_name": "Citizen User",
        "role": "citizen",
    }
    citizen_res = client.post("/api/v1/auth/register", json=citizen_payload)
    citizen_token = citizen_res.json()["access_token"]

    report_res = client.post(
        "/api/v1/waste-reports/",
        json={
            "title": "Overflowing bin",
            "description": "Plastic waste accumulated near the public bin.",
            "location": "Main Road",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "category_id": category_id,
        },
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert report_res.status_code == 200, report_res.text
    data = report_res.json()
    assert data["title"] == "Overflowing bin"
    assert data["status"] == "submitted"
