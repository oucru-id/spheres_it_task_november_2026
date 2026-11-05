"""D6: Timestamps are naive (no timezone info).

Visit timestamps from clinics in different timezones should be stored
with timezone context so cross-facility comparisons are correct.
"""
import sqlite3
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def test_timestamps_are_timezone_aware(app_client, temp_database):
    wita_visit = {
        "clinic_id": "PKM-001",
        "batch_id": "BATCH-TZ1",
        "timestamp": "2026-10-31T23:30:00",
        "patients": [
            {
                "nik": "5201141506900010",
                "name": "Adi Pratama",
                "birth_date": "1990-01-01",
                "gender": "M",
                "clinic_id": "PKM-001",
            }
        ],
        "visits": [
            {
                "patient_nik": "5201141506900010",
                "clinic_id": "PKM-001",
                "polyclinic": "umum",
                "visit_date": "2026-10-31T23:30:00",
            }
        ],
        "dispensing": [],
        "bills": [],
    }

    wib_visit = {
        "clinic_id": "PKM-003",
        "batch_id": "BATCH-TZ2",
        "timestamp": "2026-10-31T23:30:00",
        "patients": [
            {
                "nik": "3303141506900010",
                "name": "Budi Hartono",
                "birth_date": "1990-01-01",
                "gender": "M",
                "clinic_id": "PKM-003",
            }
        ],
        "visits": [
            {
                "patient_nik": "3303141506900010",
                "clinic_id": "PKM-003",
                "polyclinic": "umum",
                "visit_date": "2026-10-31T23:30:00",
            }
        ],
        "dispensing": [],
        "bills": [],
    }

    app_client.post("/batch", json=wita_visit)
    app_client.post("/batch", json=wib_visit)

    conn = sqlite3.connect(temp_database)
    rows = conn.execute(
        "SELECT visit_date, clinic_id FROM visits ORDER BY clinic_id"
    ).fetchall()
    conn.close()

    dates = {row[1]: row[0] for row in rows}

    wita_stored = dates.get("PKM-001", "")
    wib_stored = dates.get("PKM-003", "")

    has_tz = ("+" in wita_stored or "Z" in wita_stored or "UTC" in wita_stored)
    assert has_tz, (
        f"Visit timestamp should include timezone info. "
        f"PKM-001 (WITA) stored as '{wita_stored}', PKM-003 (WIB) stored as '{wib_stored}'. "
        f"Without timezone, 23:30 WITA and 23:30 WIB appear identical but are 1 hour apart."
    )
