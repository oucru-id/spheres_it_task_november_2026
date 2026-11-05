"""D1: Claim submission retry creates duplicates in the claim API.

This test submits a claim, then triggers sync. The mock API should not
have duplicate claims for the same logical claim.
"""
import sqlite3

from database import get_db


def test_no_duplicate_claims_on_retry(app_client, mock_api_client, sample_batch, temp_database):
    sample_batch["bills"] = [
        {
            "visit_id": "v-001",
            "patient_nik": "5201141506900001",
            "amount": 150000.0,
            "description": "Consultation",
        }
    ]

    app_client.post("/batch", json=sample_batch)

    app_client.post("/sync")

    import time
    time.sleep(0.5)

    app_client.post("/sync")
    time.sleep(0.5)

    claims = mock_api_client.get("/claims").json()

    claim_ids = [c["original_claim_id"] for c in claims]
    assert len(claim_ids) == len(set(claim_ids)), (
        f"Duplicate claims detected: {len(claim_ids)} total but only {len(set(claim_ids))} unique"
    )
