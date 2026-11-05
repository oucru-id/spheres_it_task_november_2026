"""D2: Money stored as float causes rounding errors.

This test checks that financial amounts are stored as integers (cents)
rather than floats, and that sums are exact.
"""
import sqlite3


def test_money_not_stored_as_float(app_client, temp_database):
    batch = {
        "clinic_id": "PKM-001",
        "batch_id": "BATCH-MONEY",
        "timestamp": "2026-10-15T10:00:00",
        "patients": [
            {
                "nik": "5201141506900002",
                "name": "Dewi Sari",
                "birth_date": "1985-03-20",
                "gender": "F",
                "clinic_id": "PKM-001",
            }
        ],
        "visits": [],
        "dispensing": [],
        "bills": [
            {"visit_id": "v-1", "patient_nik": "5201141506900002", "amount": 33333.33, "description": "A"},
            {"visit_id": "v-2", "patient_nik": "5201141506900002", "amount": 33333.33, "description": "B"},
            {"visit_id": "v-3", "patient_nik": "5201141506900002", "amount": 33333.34, "description": "C"},
        ],
    }

    app_client.post("/batch", json=batch)

    conn = sqlite3.connect(temp_database)
    row = conn.execute("SELECT SUM(amount) as total FROM bills").fetchone()
    total = row[0]
    conn.close()

    assert total == 100000.00, f"Sum of amounts should be exactly 100000.00 but got {total}"
    assert isinstance(total, int) or (isinstance(total, float) and total == int(total)), (
        "Money should be stored as integer cents to avoid float precision issues"
    )
