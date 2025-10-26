import os
import time
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost")
ENDPOINT = f"{BASE_URL}/api/v1/health/db"


def _get_with_retry(url: str, retries: int = 10, delay: float = 1.5):
    last_exc = None
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=5)
            return r
        except Exception as e:
            last_exc = e
            time.sleep(delay)
    if last_exc:
        raise last_exc


def test_health_db_ok():
    resp = _get_with_retry(ENDPOINT)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded")
    assert "postgres" in data
    assert "mongodb" in data