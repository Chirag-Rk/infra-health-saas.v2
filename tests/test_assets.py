"""Tests for the Asset API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from app.main import app
from app.database import get_db, Base

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test_urban.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_asset_payload():
    return {
        "asset_name": "Test Main Bridge",
        "asset_type": "bridge",
        "department": "Public Works",
        "latitude": 40.712,
        "longitude": -74.006,
        "installation_year": 2000,
        "status": "active",
        "last_inspection_date": "2023-06-15"
    }


class TestAssetCRUD:
    def test_create_asset(self, client, sample_asset_payload):
        resp = client.post("/assets/", json=sample_asset_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["asset_name"] == sample_asset_payload["asset_name"]
        assert data["id"] is not None
        assert "health_score" in data
        assert "risk_level" in data

    def test_list_assets(self, client, sample_asset_payload):
        client.post("/assets/", json=sample_asset_payload)
        resp = client.get("/assets/")
        assert resp.status_code == 200
        assets = resp.json()
        assert isinstance(assets, list)
        assert len(assets) >= 1

    def test_get_asset_by_id(self, client, sample_asset_payload):
        create_resp = client.post("/assets/", json=sample_asset_payload)
        asset_id = create_resp.json()["id"]
        resp = client.get(f"/assets/{asset_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == asset_id
        assert "maintenance_count" in data
        assert "citizen_report_count" in data

    def test_get_nonexistent_asset_returns_404(self, client):
        resp = client.get("/assets/99999")
        assert resp.status_code == 404

    def test_update_asset(self, client, sample_asset_payload):
        create_resp = client.post("/assets/", json=sample_asset_payload)
        asset_id = create_resp.json()["id"]
        resp = client.put(f"/assets/{asset_id}", json={"status": "under_maintenance"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "under_maintenance"

    def test_delete_asset(self, client, sample_asset_payload):
        create_resp = client.post("/assets/", json=sample_asset_payload)
        asset_id = create_resp.json()["id"]
        del_resp = client.delete(f"/assets/{asset_id}")
        assert del_resp.status_code == 204
        get_resp = client.get(f"/assets/{asset_id}")
        assert get_resp.status_code == 404

    def test_filter_by_type(self, client):
        client.post("/assets/", json={
            "asset_name": "Pipeline Test",
            "asset_type": "pipeline",
            "department": "Water",
            "latitude": 40.715,
            "longitude": -74.010,
            "installation_year": 2005,
        })
        resp = client.get("/assets/?asset_type=pipeline")
        assert resp.status_code == 200
        for a in resp.json():
            assert a["asset_type"] == "pipeline"


class TestAssetHistory:
    def test_get_history_structure(self, client, sample_asset_payload):
        create_resp = client.post("/assets/", json=sample_asset_payload)
        asset_id = create_resp.json()["id"]
        resp = client.get(f"/assets/{asset_id}/history")
        assert resp.status_code == 200
        data = resp.json()
        assert "timeline" in data
        assert "stats" in data
        assert "age_profile" in data

    def test_history_includes_construction_event(self, client, sample_asset_payload):
        create_resp = client.post("/assets/", json=sample_asset_payload)
        asset_id = create_resp.json()["id"]
        resp = client.get(f"/assets/{asset_id}/history")
        timeline = resp.json()["timeline"]
        types = [e["event_type"] for e in timeline]
        assert "construction" in types


class TestAnalyticsEndpoints:
    def test_overview_returns_summary(self, client):
        resp = client.get("/analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "total_assets" in data["summary"]

    def test_network_risk_endpoint(self, client):
        resp = client.get("/analytics/network-risk")
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "asset_risks" in data


class TestMapEndpoints:
    def test_map_assets_returns_geojson(self, client):
        resp = client.get("/map/assets")
        assert resp.status_code == 200
        data = resp.json()
        assert "geojson" in data
        assert data["geojson"]["type"] == "FeatureCollection"

    def test_nearby_assets(self, client):
        resp = client.get("/map/nearby?lat=40.712&lon=-74.006&radius_km=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "nearby_assets" in data


class TestMaintenanceEndpoints:
    def test_create_maintenance_log(self, client, sample_asset_payload):
        create_resp = client.post("/assets/", json=sample_asset_payload)
        asset_id = create_resp.json()["id"]

        log_payload = {
            "asset_id": asset_id,
            "inspection_date": "2024-03-01",
            "inspector": "James Carter",
            "condition_notes": "Surface cracks detected",
            "damage_level": 4.5,
            "maintenance_action": "Filled cracks with epoxy"
        }
        resp = client.post("/maintenance/logs/", json=log_payload)
        assert resp.status_code == 201
        assert resp.json()["inspector"] == "James Carter"

    def test_priority_list_returns_ranked_assets(self, client):
        resp = client.get("/maintenance/priority")
        assert resp.status_code == 200
        assets = resp.json()
        assert isinstance(assets, list)
        if len(assets) > 1:
            ranks = [a["rank"] for a in assets]
            assert ranks == sorted(ranks)
