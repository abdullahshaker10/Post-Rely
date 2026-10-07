"""Run with: uv run python scripts/check_readiness.py (database running)."""

import sys
import socket
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from config.settings import get_settings
from creator.main import app


with TestClient(app) as client:
    assert client.get("/").status_code == 200
    response = client.get("/ready")
    assert response.status_code == 200, response.json()
    assert response.json() == {"status": "ready"}
print("PASS: homepage and real PostgreSQL readiness")

# Reserve a local port without listening, so connections are refused.
with socket.socket() as reserved:
    reserved.bind(("127.0.0.1", 0))
    unavailable = get_settings().model_copy(
        update={"postgres_port": reserved.getsockname()[1]}
    )
    with patch("creator.main.get_settings", return_value=unavailable):
        with TestClient(app) as client:
            response = client.get("/ready")
            assert response.status_code == 503
            assert response.json() == {"status": "not_ready"}
            assert client.get("/health").json() == {"status": "ok"}
print("PASS: unavailable database returns 503 while liveness remains healthy")

invalid_credentials = get_settings().model_copy(
    update={"postgres_user": "postiz_readiness_nonexistent_user"}
)
with patch("creator.main.get_settings", return_value=invalid_credentials):
    with TestClient(app) as client:
        assert client.get("/ready").status_code == 503
print("PASS: database authentication failure returns 503")
