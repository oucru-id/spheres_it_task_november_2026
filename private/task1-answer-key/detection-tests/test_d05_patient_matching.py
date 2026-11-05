"""D5: Patient matching by NIK only merges different people who share a NIK.

Placeholder NIK 0000000000000000 should not cause patient merging.
"""
import sqlite3


def test_placeholder_nik_creates_separate_patients(app_client, temp_database):
    batch1 = {
        "clinic_id": "PKM-001",
        "batch_id": "BATCH-P1",
        "timestamp": "2026-10-15T10:00:00",
        "patients": [
            {
                "nik": "0000000000000000",
                "name": "Siti Aminah",
                "birth_date": "1988-05-12",
                "gender": "F",
                "clinic_id": "PKM-001",
            }
        ],
        "visits": [],
        "dispensing": [],
        "bills": [],
    }

    batch2 = {
        "clinic_id": "PKM-001",
        "batch_id": "BATCH-P2",
        "timestamp": "2026-10-15T10:05:00",
        "patients": [
            {
                "nik": "0000000000000000",
                "name": "Bambang Suryadi",
                "birth_date": "1975-11-03",
                "gender": "M",
                "clinic_id": "PKM-001",
            }
        ],
        "visits": [],
        "dispensing": [],
        "bills": [],
    }

    resp1 = app_client.post("/batch", json=batch1)
    resp2 = app_client.post("/batch", json=batch2)

    assert resp1.json()["patients_created"] == 1
    assert resp2.json()["patients_created"] == 1, (
        "Second patient with placeholder NIK should be created as a new patient, "
        "not matched to the first one"
    )

    conn = sqlite3.connect(temp_database)
    count = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE nik = '0000000000000000'"
    ).fetchone()[0]
    conn.close()

    assert count == 2, f"Expected 2 separate patients with placeholder NIK, got {count}"
