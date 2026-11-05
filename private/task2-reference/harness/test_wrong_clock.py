"""Test: device with wrong clock (2019) is handled gracefully."""

from conftest import load_payload


def test_wrong_clock_accepted(client):
    payload = load_payload("06-wrong-clock.json")
    resp = client.post("/sync", json=payload)
    assert resp.status_code == 200

    results = resp.json()["results"]
    for r in results:
        assert r["status"] in ("accepted", "flagged_possible_duplicate_patient"), (
            f"Record {r['client_uuid']} should be accepted despite wrong device clock, got {r['status']}"
        )


def test_server_timestamp_used(client):
    payload = load_payload("06-wrong-clock.json")
    resp = client.post("/sync", json=payload)
    data = resp.json()

    assert "server_received_at" in data
    server_time = data["server_received_at"]
    assert "2019" not in server_time, "Server should use its own clock, not the device clock"
