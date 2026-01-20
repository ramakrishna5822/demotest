import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.lightbox_api.routers.combined_router import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_combined_success_returns_200(client):
    mock_result = {"results": [{"name": "Hyderabad"}]}
    mock_status = 200

    with patch(
        "api.lightbox_api.routers.combined_router.combined_geocode_reverse_service"
    ) as mock_service:
        mock_service.return_value = (mock_result, mock_status)

        resp = client.get("/combined?street=MG%20Road&locality=Hyderabad")

        assert resp.status_code == 200
        assert resp.json() == mock_result
        mock_service.assert_called_once()

