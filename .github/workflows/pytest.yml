name: Create Tests and Run Pytest

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest fastapi uvicorn httpx

      - name: Find router file
        run: |
          echo "Searching combined_router.py..."
          find . -type f -name "combined_router.py" -print

      - name: Create test file automatically
        run: |
          mkdir -p tests/unit/routers

          ROUTER_PATH=$(find . -type f -name "combined_router.py" | head -n 1)

          if [ -z "$ROUTER_PATH" ]; then
            echo "combined_router.py not found"
            exit 1
          fi

          echo "Found router file at: $ROUTER_PATH"

          if echo "$ROUTER_PATH" | grep -q "^./api/lightbox_api/routers/combined_router.py$"; then
            IMPORT_LINE="from api.lightbox_api.routers.combined_router import router"
            PATCH_LINE="api.lightbox_api.routers.combined_router.combined_geocode_reverse_service"
          elif echo "$ROUTER_PATH" | grep -q "^./lightbox_api/routers/combined_router.py$"; then
            IMPORT_LINE="from lightbox_api.routers.combined_router import router"
            PATCH_LINE="lightbox_api.routers.combined_router.combined_geocode_reverse_service"
          elif echo "$ROUTER_PATH" | grep -q "^./src/lightbox_api/routers/combined_router.py$"; then
            IMPORT_LINE="from lightbox_api.routers.combined_router import router"
            PATCH_LINE="lightbox_api.routers.combined_router.combined_geocode_reverse_service"
          else
            echo "Unknown router location: $ROUTER_PATH"
            echo "Update YAML mapping for your folder structure."
            exit 1
          fi

          cat > tests/unit/routers/test_combined_router.py << EOF
          import pytest
          from fastapi import FastAPI
          from fastapi.testclient import TestClient
          from unittest.mock import patch

          $IMPORT_LINE


          @pytest.fixture
          def client():
              app = FastAPI()
              app.include_router(router)
              return TestClient(app)


          def test_combined_success_returns_200(client):
              mock_result = {"results": [{"name": "Hyderabad"}]}
              mock_status = 200

              with patch("$PATCH_LINE") as mock_service:
                  mock_service.return_value = (mock_result, mock_status)

                  resp = client.get("/combined?street=MG%20Road&locality=Hyderabad")

                  assert resp.status_code == 200
                  assert resp.json() == mock_result
                  mock_service.assert_called_once()
          EOF

      - name: Run tests
        run: |
          if [ -d "src" ]; then
            export PYTHONPATH=$(pwd)/src
          else
            export PYTHONPATH=$(pwd)
          fi
          pytest -q tests
