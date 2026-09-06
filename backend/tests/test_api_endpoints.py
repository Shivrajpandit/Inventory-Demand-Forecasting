"""
FastAPI REST API Integration & Endpoint Tests
==============================================
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import Base, engine


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Validates /health endpoint."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"


def test_auth_registration_and_login(client):
    """Validates user registration, login, and JWT token issuance."""
    unique_email = f"planner_{uuid.uuid4().hex[:8]}@example.com"
    # Register
    reg_payload = {
        "email": unique_email,
        "password": "strongpassword123",
        "full_name": "Test Planner",
        "role": "inventory_planner",
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    token_data = reg_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Test /me with Bearer token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_email

    # Login
    login_res = client.post("/api/auth/login", json={"email": unique_email, "password": "strongpassword123"})
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_get_catalog_products_and_stores(client):
    """Validates /api/products and /api/stores."""
    p_res = client.get("/api/products")
    assert p_res.status_code == 200
    products = p_res.json()
    assert len(products) > 0

    s_res = client.get("/api/stores")
    assert s_res.status_code == 200
    stores = s_res.json()
    assert len(stores) > 0


def test_dashboard_summary(client):
    """Validates /api/dashboard/summary."""
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_sales_volume" in data
    assert "champion_model_name" in data
    assert len(data["category_distribution"]) > 0


def test_forecast_generation_endpoint(client):
    """Validates POST /api/forecast."""
    payload = {
        "store_id": "STR_01",
        "product_id": "PRD_01",
        "horizon_days": 14,
        "demand_growth_pct": 10.0,
    }
    res = client.post("/api/forecast", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["store_id"] == "STR_01"
    assert data["product_id"] == "PRD_01"
    assert len(data["daily_forecasts"]) == 14
    assert data["total_forecast_demand"] > 0


def test_inventory_status_endpoint(client):
    """Validates GET /api/inventory/status."""
    res = client.get("/api/inventory/status?store_id=STR_01")
    assert res.status_code == 200
    data = res.json()
    assert "total_products_tracked" in data
    assert len(data["items"]) > 0
    first_item = data["items"][0]
    assert "reorder_point" in first_item
    assert "risk_status" in first_item


def test_scenario_simulation_endpoint(client):
    """Validates POST /api/scenario/simulate."""
    payload = {
        "store_id": "STR_01",
        "product_id": "PRD_01",
        "demand_growth_pct": 20.0,
        "service_level": 0.99,
        "lead_time_days": 7,
        "horizon_days": 7,
    }
    res = client.post("/api/scenario/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "comparison" in data
    assert data["comparison"]["total_forecast_demand"]["scenario"] > data["comparison"]["total_forecast_demand"]["baseline"]


def test_models_performance_and_champion(client):
    """Validates /api/models/performance and /api/models/champion."""
    p_res = client.get("/api/models/performance")
    assert p_res.status_code == 200
    assert len(p_res.json()) > 0

    c_res = client.get("/api/models/champion")
    assert c_res.status_code == 200
    c_data = c_res.json()
    assert "model_name" in c_data
    assert "metrics" in c_data
