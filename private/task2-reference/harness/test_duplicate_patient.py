"""Test: near-duplicate patients are flagged, not auto-merged."""

from conftest import load_payload


def test_duplicate_patient_flagged(client):
    payload1 = load_payload("01-normal-batch.json")
    client.post("/sync", json=payload1)

    payload2 = load_payload("04-duplicate-patients.json")
    resp = client.post("/sync", json=payload2)
    assert resp.status_code == 200
    results = resp.json()["results"]

    statuses = {r["client_uuid"]: r["status"] for r in results}

    siti_status = statuses.get("pat-b001-uuid")
    siti_upper_status = statuses.get("pat-b002-uuid")

    flagged_count = sum(1 for s in statuses.values() if s == "flagged_possible_duplicate_patient")
    assert flagged_count >= 1, "At least one near-duplicate patient should be flagged"


def test_flagged_patient_in_review_queue(client):
    payload1 = load_payload("01-normal-batch.json")
    client.post("/sync", json=payload1)

    payload2 = load_payload("04-duplicate-patients.json")
    client.post("/sync", json=payload2)

    resp = client.get("/review-queue")
    assert resp.status_code == 200
    items = resp.json()["items"]

    patient_flags = [i for i in items if i["type"] == "possible_duplicate_patient"]
    assert len(patient_flags) >= 1, "Flagged patients should appear in review queue"


def test_flagged_patient_still_created(client):
    payload1 = load_payload("01-normal-batch.json")
    client.post("/sync", json=payload1)

    payload2 = load_payload("04-duplicate-patients.json")
    resp = client.post("/sync", json=payload2)
    results = resp.json()["results"]

    flagged = [r for r in results if r["status"] == "flagged_possible_duplicate_patient"]
    for f in flagged:
        assert "server_id" in f, "Flagged patient should still be created with a server_id"
        patient_resp = client.get(f"/patients/{f['server_id']}")
        assert patient_resp.status_code == 200
