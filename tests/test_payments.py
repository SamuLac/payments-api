"""
Tests - Payments API

Run with:
    pytest tests/ -v

Uses an in-memory SQLite database so you don't need PostgreSQL to run tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use SQLite in-memory for tests — no need for a real database
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_payment():
    """Creates a payment and returns its data for use in other tests."""
    payload = {
        "description": "Test payment - Plan Pro",
        "amount": 99.90,
        "method": "pix",
        "payer_name": "Samuel Lacerda",
        "payer_email": "samuel@test.com",
    }
    response = client.post("/payments", json=payload)
    assert response.status_code == 201
    return response.json()


# ─── Health check ─────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ─── Create Payment ───────────────────────────────────────────────────────────

def test_create_payment_success():
    payload = {
        "description": "Monthly subscription",
        "amount": 49.90,
        "method": "credit_card",
        "payer_name": "João Silva",
        "payer_email": "joao@email.com",
    }
    response = client.post("/payments", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["status"] == "pending"
    assert data["amount"] == 49.90
    assert "id" in data


def test_create_payment_invalid_amount():
    """Amount must be greater than 0."""
    payload = {
        "description": "Invalid payment",
        "amount": -10,
        "method": "pix",
        "payer_name": "Test",
        "payer_email": "test@email.com",
    }
    response = client.post("/payments", json=payload)
    assert response.status_code == 422


def test_create_payment_invalid_email():
    payload = {
        "description": "Invalid email test",
        "amount": 50.0,
        "method": "pix",
        "payer_name": "Test",
        "payer_email": "not-an-email",
    }
    response = client.post("/payments", json=payload)
    assert response.status_code == 422


# ─── Get Payment ──────────────────────────────────────────────────────────────

def test_get_payment_success(sample_payment):
    payment_id = sample_payment["id"]
    response = client.get(f"/payments/{payment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_get_payment_not_found():
    response = client.get("/payments/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# ─── Update Payment Status ────────────────────────────────────────────────────

def test_update_payment_to_completed(sample_payment):
    payment_id = sample_payment["id"]
    response = client.patch(f"/payments/{payment_id}", json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_update_payment_invalid_transition(sample_payment):
    """pending -> refunded is not allowed."""
    payment_id = sample_payment["id"]
    response = client.patch(f"/payments/{payment_id}", json={"status": "refunded"})
    assert response.status_code == 422


# ─── List Payments ────────────────────────────────────────────────────────────

def test_list_payments():
    response = client.get("/payments")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data


def test_list_payments_filter_by_status():
    response = client.get("/payments?status=pending")
    assert response.status_code == 200


# ─── Delete Payment ───────────────────────────────────────────────────────────

def test_delete_pending_payment(sample_payment):
    payment_id = sample_payment["id"]
    response = client.delete(f"/payments/{payment_id}")
    assert response.status_code == 204


def test_delete_completed_payment():
    """Completed payments cannot be deleted."""
    payload = {
        "description": "Payment to complete",
        "amount": 20.0,
        "method": "pix",
        "payer_name": "Ana Lima",
        "payer_email": "ana@email.com",
    }
    create_resp = client.post("/payments", json=payload)
    payment_id = create_resp.json()["id"]

    client.patch(f"/payments/{payment_id}", json={"status": "completed"})

    delete_resp = client.delete(f"/payments/{payment_id}")
    assert delete_resp.status_code == 422
