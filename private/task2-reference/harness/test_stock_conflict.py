"""Test: two devices dispensing the same last stock.

Stock should go negative (dispensing is never refused),
and negative stock should appear in the review queue.
"""

from conftest import load_payload


def test_stock_goes_negative(client):
    payload = load_payload("05-stock-conflict.json")
    resp = client.post("/sync", json=payload)
    assert resp.status_code == 200

    results = resp.json()["results"]
    disp_statuses = [r for r in results if r["client_uuid"].startswith("disp-c")]
    for d in disp_statuses:
        assert d["status"] == "accepted", f"Dispensing should be accepted even when stock goes negative"

    stock_resp = client.get("/stock/MED-003")
    assert stock_resp.status_code == 200
    current = stock_resp.json()["current_stock"]
    assert current < 0, f"MED-003 started at 20, dispensed 15+10=25, should be -5, got {current}"


def test_negative_stock_in_review_queue(client):
    payload = load_payload("05-stock-conflict.json")
    client.post("/sync", json=payload)

    resp = client.get("/review-queue")
    items = resp.json()["items"]
    stock_flags = [i for i in items if i["type"] == "negative_stock"]
    assert len(stock_flags) >= 1, "Negative stock should appear in review queue"

    med3_flags = [i for i in stock_flags if i["medicine_id"] == "MED-003"]
    assert len(med3_flags) >= 1


def test_stock_updates_in_response(client):
    payload = load_payload("05-stock-conflict.json")
    resp = client.post("/sync", json=payload)
    data = resp.json()

    assert "stock_updates" in data
    med3_updates = [s for s in data["stock_updates"] if s["medicine_id"] == "MED-003"]
    assert len(med3_updates) >= 1, "Response should include stock update for MED-003"
