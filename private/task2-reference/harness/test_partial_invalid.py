"""Test: partially invalid batch returns 200 with per-record statuses."""

from conftest import load_payload


def test_partial_invalid_returns_200(client):
    payload = load_payload("03-partial-invalid.json")
    resp = client.post("/sync", json=payload)
    assert resp.status_code == 200


def test_partial_invalid_per_record_status(client):
    payload = load_payload("03-partial-invalid.json")
    resp = client.post("/sync", json=payload)
    results = resp.json()["results"]

    statuses = {r["client_uuid"]: r["status"] for r in results}

    assert statuses["pat-a010-uuid"] == "accepted"
    assert statuses["pat-invalid-001"] == "rejected"
    assert statuses["vis-a010-uuid"] == "accepted"
    assert statuses["disp-a010-uuid"] == "accepted"


def test_partial_invalid_has_reasons(client):
    payload = load_payload("03-partial-invalid.json")
    resp = client.post("/sync", json=payload)
    results = resp.json()["results"]

    rejected = [r for r in results if r["status"] == "rejected"]
    for r in rejected:
        assert "reason" in r, f"Rejected record {r['client_uuid']} missing reason"
