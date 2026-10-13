import pytest
import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.cache import price_cache
from app.scrapers.base import SourceResult
from app.scrapers.manager import ScraperManager

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data

def test_unauthorized_access():
    response = client.get("/api/v1/usd")
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]["message"]

def test_authorized_with_header():
    # Warmup cache if empty
    if not price_cache.has_data:
        price_cache.set({
            "status": "success",
            "currency": "USD",
            "unit": "toman",
            "price": 257400,
            "buy": 257200,
            "sell": 257400,
            "price_rial": 2574000,
            "active_source": "bonbast",
            "active_source_name": "Bonbast",
            "updated_at": "2026-10-13T12:00:00Z",
            "sources": {}
        })

    response = client.get("/api/v1/usd", headers={"X-API-Key": settings.API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"
    assert data["price"] > 0
    assert data["unit"] == "toman"
    assert data["cached"] is True
    assert "cache_age_seconds" in data

def test_authorized_with_query_param():
    response = client.get(f"/api/v1/usd?api_key={settings.API_KEY}")
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"

def test_authorized_with_bearer_token():
    response = client.get("/api/v1/usd", headers={"Authorization": f"Bearer {settings.API_KEY}"})
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"

def test_simple_mode():
    response = client.get(f"/api/v1/usd?simple=1&api_key={settings.API_KEY}")
    assert response.status_code == 200
    data = response.json()
    assert "price" in data
    assert "unit" in data
    assert "sources" not in data  # compact view

def test_fallback_logic():
    manager = ScraperManager()
    assert len(manager.scrapers) >= 5
    # Check priorities are ascending
    priorities = [s.priority for s in manager.scrapers]
    assert priorities == sorted(priorities)
