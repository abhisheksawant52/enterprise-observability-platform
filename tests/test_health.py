"""Tests for the operational HTTP endpoints."""

from fastapi.testclient import TestClient

from obsplatform.config import Settings
from obsplatform.main import create_app


def _client() -> TestClient:
    settings = Settings(service_name="test-platform", env="test")
    return TestClient(create_app(settings))


def test_health_ok() -> None:
    with _client() as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_reports_service_name() -> None:
    with _client() as client:
        response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["service"] == "test-platform"


def test_metrics_endpoint_exposes_prometheus_format() -> None:
    with _client() as client:
        client.get("/health")
        response = client.get("/metrics")
    assert response.status_code == 200
    assert "obsplatform_requests_total" in response.text
