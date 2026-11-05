"""Test: records with old/unknown schema versions are handled per contract."""

from conftest import load_payload


def test_old_schema_version_handling(client):
    payload = load_payload("07-old-schema-version.json")
    resp = client.post("/sync", json=payload)
    assert resp.status_code == 200

    results = resp.json()["results"]
    statuses = {r["client_uuid"]: r for r in results}

    future_version = statuses.get("vis-e001-uuid")
    assert future_version is not None
    assert future_version["status"] == "rejected", (
        "Unknown future schema_version should be rejected"
    )
    assert "schema_version" in future_version.get("reason", "").lower() or "schema" in future_version.get("reason", "").lower(), (
        "Rejection reason should mention schema version"
    )
