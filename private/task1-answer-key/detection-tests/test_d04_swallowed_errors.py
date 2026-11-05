"""D4: Failed claim submissions are still marked as synced.

This test checks that when a claim submission fails, it is NOT marked
as synced.
"""
import sqlite3
import os

import httpx


def test_failed_claim_not_marked_synced(app_client, temp_database):
    os.environ["CLAIM_API_URL"] = "http://localhost:19999"

    import config
    original_url = config.CLAIM_API_URL
    config.CLAIM_API_URL = "http://localhost:19999"

    try:
        batch = {
            "clinic_id": "PKM-001",
            "batch_id": "BATCH-FAIL",
            "timestamp": "2026-10-15T10:00:00",
            "patients": [
                {
                    "nik": "5201141506900004",
                    "name": "Rina Wati",
                    "birth_date": "1992-07-10",
                    "gender": "F",
                    "clinic_id": "PKM-001",
                }
            ],
            "visits": [],
            "dispensing": [],
            "bills": [
                {"visit_id": "v-1", "patient_nik": "5201141506900004", "amount": 100000.0, "description": "Test"},
            ],
        }

        app_client.post("/batch", json=batch)

        import app as app_module
        original_token = getattr(app_module, '_token', None)
        app_module._token = "fake-expired-token"

        try:
            from app import sync_pending_claims
            sync_pending_claims()
        except Exception:
            pass

        conn = sqlite3.connect(temp_database)
        row = conn.execute("SELECT synced, status FROM claims").fetchone()
        conn.close()

        assert row[0] == 0, "Failed claim should NOT be marked as synced"
        assert row[1] != "synced", f"Failed claim status should not be 'synced', got '{row[1]}'"

    finally:
        config.CLAIM_API_URL = original_url
        import app as app_module
        app_module._token = None
