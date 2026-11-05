"""Test: duplicate batch returns same results, no side effects."""

from conftest import load_payload


def test_batch_idempotency(client):
    payload = load_payload("01-normal-batch.json")

    resp1 = client.post("/sync", json=payload)
    assert resp1.status_code == 200
    data1 = resp1.json()

    resp2 = client.post("/sync", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()

    assert data1["batch_id"] == data2["batch_id"]
    assert len(data1["results"]) == len(data2["results"])

    for r1, r2 in zip(data1["results"], data2["results"]):
        assert r1["client_uuid"] == r2["client_uuid"]


def test_record_uuid_idempotency(client):
    payload = load_payload("01-normal-batch.json")
    client.post("/sync", json=payload)

    single_record = payload["records"][0]
    new_batch = {
        "device_id": payload["device_id"],
        "batch_id": "batch-resend-single",
        "records": [single_record],
    }

    resp = client.post("/sync", json=new_batch)
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert results[0]["status"] == "duplicate"
