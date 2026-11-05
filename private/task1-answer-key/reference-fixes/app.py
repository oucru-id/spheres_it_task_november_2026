import hashlib
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks

from config import CLAIM_API_URL, SYNC_BATCH_SIZE, SYNC_INTERVAL_SECONDS
from database import init_db, get_db
from models import BatchPayload, BatchResponse, HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("clinic_sync")

_token: str | None = None
_token_expires_at: float = 0


# ── Token management ────────────────────────────────────────────────────

def fetch_token() -> str:
    global _token, _token_expires_at
    resp = httpx.post(f"{CLAIM_API_URL}/token", json={"client_id": "clinic-sync"})
    resp.raise_for_status()
    data = resp.json()
    _token = data["access_token"]
    _token_expires_at = time.time() + data["expires_in"] - 30
    logger.info("Obtained new claim API token")
    return _token


def get_token() -> str:
    global _token, _token_expires_at
    if _token is None or time.time() >= _token_expires_at:
        return fetch_token()
    return _token


# ── Patient matching ────────────────────────────────────────────────────

PLACEHOLDER_NIKS = {"0000000000000000"}


def get_or_create_patient(conn, patient) -> str:
    if patient.nik not in PLACEHOLDER_NIKS:
        row = conn.execute(
            "SELECT id FROM patients WHERE nik = ? AND name = ? AND birth_date = ?",
            (patient.nik, patient.name, patient.birth_date),
        ).fetchone()
        if row:
            return row["id"]

    patient_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO patients (id, nik, name, birth_date, gender, address, clinic_id, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (patient_id, patient.nik, patient.name, patient.birth_date,
         patient.gender, patient.address, patient.clinic_id, now),
    )
    return patient_id


# ── Visit recording ─────────────────────────────────────────────────────

def get_clinic_timezone(conn, clinic_id: str) -> str:
    row = conn.execute("SELECT timezone FROM clinics WHERE id = ?", (clinic_id,)).fetchone()
    return row["timezone"] if row else "UTC"


def normalize_timestamp(visit_date: str, clinic_tz: str) -> str:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            dt = datetime.strptime(visit_date, fmt)
            break
        except ValueError:
            continue
    else:
        return visit_date

    if fmt.endswith("Z"):
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        tz = ZoneInfo(clinic_tz)
        dt = dt.replace(tzinfo=tz)

    return dt.astimezone(timezone.utc).isoformat()


def record_visit(conn, visit, patient_id: str) -> str:
    visit_id = str(uuid.uuid4())
    clinic_tz = get_clinic_timezone(conn, visit.clinic_id)
    normalized_date = normalize_timestamp(visit.visit_date, clinic_tz)

    reg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO registrations (id, registration_number, patient_id, clinic_id, registered_at, status, polyclinic) "
        "VALUES (?, ?, ?, ?, ?, 'active', ?)",
        (reg_id, f"REG-{uuid.uuid4().hex[:8].upper()}", patient_id,
         visit.clinic_id, now, visit.polyclinic),
    )
    conn.execute(
        "INSERT INTO visits (id, registration_id, patient_id, clinic_id, polyclinic, visit_date, diagnosis, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (visit_id, reg_id, patient_id, visit.clinic_id,
         visit.polyclinic, normalized_date, visit.diagnosis, visit.notes),
    )
    return visit_id


# ── Dispensing ───────────────────────────────────────────────────────────

def dispense_medicine(conn, record, patient_id: str):
    updated = conn.execute(
        "UPDATE medicines SET stock = stock - ? WHERE id = ? AND stock >= ?",
        (record.quantity, record.medicine_id, record.quantity),
    ).rowcount
    if updated == 0:
        current = conn.execute(
            "SELECT stock FROM medicines WHERE id = ?", (record.medicine_id,)
        ).fetchone()
        if current is None:
            raise ValueError(f"Medicine {record.medicine_id} not found")
        raise ValueError(
            f"Insufficient stock for {record.medicine_id}: "
            f"requested {record.quantity}, available {current['stock']}"
        )

    disp_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO dispensing (id, visit_id, patient_id, medicine_id, quantity, dispensed_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (disp_id, record.visit_id, patient_id, record.medicine_id, record.quantity, now),
    )


# ── Billing / claims ────────────────────────────────────────────────────

def create_bill_and_claim(conn, bill, patient_id: str):
    bill_id = str(uuid.uuid4())
    claim_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    conn.execute(
        "INSERT INTO bills (id, visit_id, patient_id, amount, description, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (bill_id, bill.visit_id, patient_id, bill.amount, bill.description, now),
    )
    conn.execute(
        "INSERT INTO claims (id, bill_id, patient_id, claim_amount, status, synced, created_at) "
        "VALUES (?, ?, ?, ?, 'pending', 0, ?)",
        (claim_id, bill_id, patient_id, bill.amount, now),
    )


# ── Claim submission with idempotency ───────────────────────────────────

def generate_claim_reference(claim_id: str) -> str:
    return hashlib.sha256(f"claim-{claim_id}".encode()).hexdigest()[:16]


def submit_claim_to_api(claim_id: str, claim_amount: int, patient_id: str) -> dict | None:
    token = get_token()
    claim_ref = generate_claim_reference(claim_id)

    max_retries = 5
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            resp = httpx.post(
                f"{CLAIM_API_URL}/claims",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "claim_reference": claim_ref,
                    "claim_id": claim_id,
                    "amount": claim_amount,
                    "patient_id": patient_id,
                },
                timeout=10.0,
            )

            if resp.status_code == 401:
                token = fetch_token()
                continue

            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", base_delay * (2 ** attempt)))
                logger.warning("Rate limited by claim API, retrying after %.1fs", retry_after)
                time.sleep(retry_after)
                continue

            resp.raise_for_status()
            return resp.json()

        except httpx.TimeoutException:
            delay = base_delay * (2 ** attempt)
            logger.warning(
                "Claim submission timed out (attempt %d/%d), retrying in %.1fs",
                attempt + 1, max_retries, delay,
            )
            time.sleep(delay)

        except httpx.HTTPStatusError as e:
            logger.error("Claim submission failed with status %d", e.response.status_code)
            return None

    logger.error("Claim submission exhausted retries for claim %s", claim_id)
    return None


# ── Sync pending claims ─────────────────────────────────────────────────

def sync_pending_claims():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, claim_amount, patient_id FROM claims WHERE synced = 0 LIMIT ?",
            (SYNC_BATCH_SIZE,),
        ).fetchall()

        if not rows:
            return

        logger.info("Syncing %d pending claims", len(rows))

        for row in rows:
            result = submit_claim_to_api(row["id"], row["claim_amount"], row["patient_id"])
            if result:
                conn.execute(
                    "UPDATE claims SET synced = 1, external_claim_id = ?, "
                    "submitted_at = ?, status = 'synced' WHERE id = ?",
                    (result.get("claim_id"), datetime.now(timezone.utc).isoformat(), row["id"]),
                )
                conn.commit()
            else:
                conn.execute(
                    "UPDATE claims SET status = 'failed' WHERE id = ?",
                    (row["id"],),
                )
                conn.commit()
                logger.error("Failed to sync claim %s — marked as failed", row["id"])


# ── FastAPI app ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(title="Clinic Sync Service", version="1.0.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/batch", response_model=BatchResponse)
def receive_batch(payload: BatchPayload):
    logger.info(
        "Received batch %s from clinic %s: %d patients, %d visits, %d dispensing, %d bills",
        payload.batch_id, payload.clinic_id,
        len(payload.patients), len(payload.visits),
        len(payload.dispensing), len(payload.bills),
    )

    patients_created = 0
    patients_existing = 0
    visits_recorded = 0
    dispensing_recorded = 0
    bills_created = 0
    claims_created = 0
    errors = []

    with get_db() as conn:
        clinic = conn.execute(
            "SELECT id FROM clinics WHERE id = ?", (payload.clinic_id,)
        ).fetchone()
        if not clinic:
            raise HTTPException(status_code=400, detail=f"Unknown clinic: {payload.clinic_id}")

        patient_map = {}

        for p in payload.patients:
            try:
                existing = None
                if p.nik not in PLACEHOLDER_NIKS:
                    existing = conn.execute(
                        "SELECT id FROM patients WHERE nik = ? AND name = ? AND birth_date = ?",
                        (p.nik, p.name, p.birth_date),
                    ).fetchone()

                if existing:
                    patient_map[p.nik] = existing["id"]
                    patients_existing += 1
                else:
                    pid = get_or_create_patient(conn, p)
                    patient_map[p.nik] = pid
                    patients_created += 1
            except Exception as e:
                errors.append(f"Patient {p.nik[:4]}****: {e}")

        for v in payload.visits:
            try:
                pid = patient_map.get(v.patient_nik)
                if not pid:
                    errors.append(f"Visit skipped: patient not found for NIK {v.patient_nik[:4]}****")
                    continue
                vid = record_visit(conn, v, pid)
                visits_recorded += 1
            except Exception as e:
                errors.append(f"Visit recording error: {e}")

        for d in payload.dispensing:
            try:
                pid = patient_map.get(d.patient_nik)
                if not pid:
                    errors.append(f"Dispensing skipped: patient not found")
                    continue
                dispense_medicine(conn, d, pid)
                dispensing_recorded += 1
            except ValueError as e:
                errors.append(str(e))

        for b in payload.bills:
            try:
                pid = patient_map.get(b.patient_nik)
                if not pid:
                    errors.append(f"Bill skipped: patient not found")
                    continue
                create_bill_and_claim(conn, b, pid)
                bills_created += 1
                claims_created += 1
            except Exception as e:
                errors.append(f"Bill creation error: {e}")

        conn.commit()

    return BatchResponse(
        batch_id=payload.batch_id,
        patients_created=patients_created,
        patients_existing=patients_existing,
        visits_recorded=visits_recorded,
        dispensing_recorded=dispensing_recorded,
        bills_created=bills_created,
        claims_created=claims_created,
        errors=errors,
    )


@app.post("/sync")
def trigger_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_pending_claims)
    return {"status": "sync_triggered"}


@app.get("/claims")
def list_claims(status: str | None = None, limit: int = 100):
    with get_db() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM claims WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM claims ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


@app.get("/patients")
def list_patients(clinic_id: str | None = None, limit: int = 100):
    with get_db() as conn:
        if clinic_id:
            rows = conn.execute(
                "SELECT id, nik, name, birth_date, gender, clinic_id FROM patients "
                "WHERE clinic_id = ? LIMIT ?",
                (clinic_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, nik, name, birth_date, gender, clinic_id FROM patients LIMIT ?",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


@app.get("/stock")
def list_stock():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM medicines").fetchall()
    return [dict(r) for r in rows]
