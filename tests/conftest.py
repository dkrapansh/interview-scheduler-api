import os

os.environ["DATABASE_URL"] = "sqlite:///./test_interview.db"
os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"
os.environ["TESTING"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

TEST_DB_URL = "sqlite:///./test_interview.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
app.dependency_overrides[get_db] = override_get_db

# clean slate before every test
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

# fixture core
@pytest.fixture
def client():
    return TestClient(app)

# Helpers to be called inside test functions
def register_user(client, full_name, email, password, role):
    return client.post("/users/", json={
        "full_name": full_name,
        "email": email,
        "password": password,
        "role": role,
    })

def login(client, email, password):
    return client.post("/auth/login", json={
        "email": email, 
        "password": password,
    })

def auth_headers(client, email, password):
    res = login(client, email, password)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_job(client, headers, title="Backend Engineer", description="Python role"):
    return client.post("/jobs/", json={
        "title": title,
        "description": description,
    }, headers=headers)

def create_slot(client, headers, job_id, start_iso, end_iso):
    return client.post("/slots/", json={
        "job_id": job_id,
        "start_time": start_iso,
        "end_time": end_iso,
    }, headers=headers)