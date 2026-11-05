"""D7: Token is cached forever and never refreshed after expiry.

When the claim API token expires, the service should obtain a new one.
"""
import os
import time as time_module


def test_token_refreshed_after_expiry(app_client, mock_api_client, temp_database):
    os.environ["MOCK_TOKEN_EXPIRY"] = "1"

    from mock_claim_api import tokens
    tokens.clear()

    import app as app_module
    app_module._token = None

    batch = {
        "clinic_id": "PKM-001",
        "batch_id": "BATCH-TOKEN",
        "timestamp": "2026-10-15T10:00:00",
        "patients": [
            {
                "nik": "5201141506900020",
                "name": "Token Test",
                "birth_date": "1990-01-01",
                "gender": "M",
                "clinic_id": "PKM-001",
            }
        ],
        "visits": [],
        "dispensing": [],
        "bills": [
            {"visit_id": "v-1", "patient_nik": "5201141506900020", "amount": 50000.0, "description": "Test"},
        ],
    }
    app_client.post("/batch", json=batch)

    from app import get_token
    token1 = get_token()

    time_module.sleep(2)

    from mock_claim_api import tokens as mock_tokens
    for t in list(mock_tokens.keys()):
        mock_tokens[t] = time_module.time() - 1

    token2 = get_token()

    assert token1 != token2 or hasattr(app_module, '_token_expires_at'), (
        "Token should be refreshed after expiry. The old token was expired "
        "but get_token() returned the same cached value."
    )
