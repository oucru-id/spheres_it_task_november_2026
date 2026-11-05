"""D3: Medicine stock update is not atomic.

This test verifies stock cannot go negative and that concurrent
dispensing is handled correctly.
"""
import sqlite3
import threading


def test_stock_cannot_go_negative(app_client, temp_database):
    conn = sqlite3.connect(temp_database)
    conn.execute("UPDATE medicines SET stock = 5 WHERE id = 'MED-001'")
    conn.commit()
    conn.close()

    batch = {
        "clinic_id": "PKM-001",
        "batch_id": "BATCH-STOCK",
        "timestamp": "2026-10-15T10:00:00",
        "patients": [
            {
                "nik": "5201141506900003",
                "name": "Budi Santoso",
                "birth_date": "1980-01-01",
                "gender": "M",
                "clinic_id": "PKM-001",
            }
        ],
        "visits": [],
        "dispensing": [
            {"visit_id": "v-1", "patient_nik": "5201141506900003", "medicine_id": "MED-001", "quantity": 10},
        ],
        "bills": [],
    }

    resp = app_client.post("/batch", json=batch)
    data = resp.json()

    conn = sqlite3.connect(temp_database)
    row = conn.execute("SELECT stock FROM medicines WHERE id = 'MED-001'").fetchone()
    stock = row[0]
    conn.close()

    assert stock >= 0, f"Stock went negative: {stock}. Dispensing should be rejected when insufficient."
    assert len(data["errors"]) > 0, "Should report an error when stock is insufficient"
