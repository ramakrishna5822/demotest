name: Unit Tests - Combined Router

on:
  push:
    branches: [ "main" ]
  pull_request:

jobs:
  unit-tests:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install fastapi uvicorn pytest httpx

      - name: Find router and create unit test
        run: |
          mkdir -p tests/unit/routers

          # Find combined_router.py file
          ROUTER_PATH=$(find . -name "combined_router.py" | head -n 1)

          if [ -z "$ROUTER_PATH" ]; then
            echo "combined_router.py not found!"
            exit 1
          fi

          echo "Found router file at: $ROUTER_PATH"

          # Mapping for different project structures
          if echo "$ROUTER_PATH" | grep -q "^./api/lightbox_api/routers/combined_router.py$"; then
            IMPORT_LINE="from api.lightbox_api.routers.combined_router import router"
            PATCH_LINE="api.lightbox_api.routers.combined_router.combined_geocode_reverse_service"

          elif echo "$ROUTER_PATH" | grep -q "^./lightbox_api/routers/combined_router.py$"; then
            IMPORT_LINE="from lightbox_api.routers.combined_router import router"
            PATCH_LINE="lightbox_api.routers.combined_router.combined_geocode_reverse_service"

          elif echo "$ROUTER_PATH" | grep -q "^./src/lightbox_api/routers/combined_router.py$"; then
            IMPORT_LINE="from lightbox_api.routers.combined_router import router"
            PATCH_LINE="lightbox_api.routers.combined_router.combined_geocode_reverse_service"

          elif echo "$ROUTER_PATH" | grep -q "^./combined_router.py$"; then
            IMPORT_LINE="from combined_router import router"
            PATCH_LINE="combined_router.combined_geocode_reverse_service"

          else
            echo "Unknown router location: $ROUTER_PATH"
            echo "Update YAML mapping for your folder structure."
            exit 1
          fi

          # Create test file
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

          echo "✅ Unit test created successfully!"

      - name: Run Pytest
        run: |
          pytest -v
