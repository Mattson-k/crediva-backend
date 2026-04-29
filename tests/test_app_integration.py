from fastapi.testclient import TestClient

from app.main import app


def test_frontend_shell_serves() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "License renewal intelligence" in response.text
    assert response.headers["cache-control"] == "no-store"


def test_frontend_config_serves_api_base() -> None:
    with TestClient(app) as client:
        response = client.get("/config")

    assert response.status_code == 200
    assert "apiBaseUrl" in response.json()


def test_cors_allows_configured_origin() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/licenses",
            headers={
                "Origin": "http://127.0.0.1:8000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:8000"


def test_static_assets_are_cacheable() -> None:
    with TestClient(app) as client:
        response = client.get("/static/app.js")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=3600"
