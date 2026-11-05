import json
import os

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
PAYLOADS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "candidate", "task2-offline-sync", "sample-payloads"
)

RESET_DATA = {
    "clinics": [
        {"id": "PKM-001", "name": "Puskesmas Sandik Raya", "timezone": "Asia/Makassar"},
        {"id": "PKM-002", "name": "Puskesmas Gunungsari Timur", "timezone": "Asia/Makassar"},
        {"id": "PKM-003", "name": "Puskesmas Kalimanah Wetan", "timezone": "Asia/Jakarta"},
    ],
    "stock": [
        {"medicine_id": "MED-001", "name": "Paracetamol 500mg", "quantity": 5000},
        {"medicine_id": "MED-002", "name": "Amoxicillin 500mg", "quantity": 3000},
        {"medicine_id": "MED-003", "name": "ORS (Oralit)", "quantity": 20},
    ],
}


@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30.0)


@pytest.fixture(autouse=True)
def reset_server(client):
    resp = client.post("/reset", json=RESET_DATA)
    assert resp.status_code == 200


def load_payload(name: str) -> dict:
    with open(os.path.join(PAYLOADS_DIR, name)) as f:
        return json.load(f)
