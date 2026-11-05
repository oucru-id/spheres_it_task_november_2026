"""D10: PII and health data (NIK, name, diagnosis) appear in log output.

Log messages should not contain identifiable patient information.
"""
import logging
import io

from app import get_or_create_patient, record_visit
from database import init_db, get_db


def test_no_pii_in_logs(temp_database):
    init_db()

    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger("clinic_sync")
    logger.addHandler(handler)

    try:
        from models import PatientRecord, VisitRecord

        patient = PatientRecord(
            nik="5201141506900099",
            name="Rahmat Hidayat",
            birth_date="1985-12-25",
            gender="M",
            address="Jl. Merdeka 17",
            clinic_id="PKM-001",
        )

        with get_db() as conn:
            pid = get_or_create_patient(conn, patient)
            conn.commit()

        visit = VisitRecord(
            patient_nik="5201141506900099",
            clinic_id="PKM-001",
            polyclinic="umum",
            visit_date="2026-10-15T09:00:00",
            diagnosis="Diabetes mellitus type 2",
        )

        with get_db() as conn:
            record_visit(conn, visit, pid)
            conn.commit()

        log_output = log_capture.getvalue()

        assert "5201141506900099" not in log_output, (
            f"Patient NIK appears in logs. This is PII that should not be logged."
        )
        assert "Rahmat Hidayat" not in log_output, (
            f"Patient name appears in logs. This is PII that should not be logged."
        )
        assert "Diabetes mellitus" not in log_output, (
            f"Patient diagnosis appears in logs. This is protected health information."
        )

    finally:
        logger.removeHandler(handler)
