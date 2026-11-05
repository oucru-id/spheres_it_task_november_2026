"""Reference implementation for Task 2: Offline-First Sync endpoint."""

import uuid
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Offline Sync Reference", version="1.0.0")

# In-memory storage
clinics: dict[str, dict] = {}
stock: dict[str, dict] = {}
patients: dict[str, dict] = {}
visits: dict[str, dict] = {}
dispensing_records: dict[str, dict] = {}
seen_uuids: dict[str, dict] = {}
seen_batches: dict[str, dict] = {}
review_queue: list[dict] = []
client_to_server: dict[str, str] = {}


class ResetRequest(BaseModel):
    clinics: list[dict]
    stock: list[dict]


class SyncRequest(BaseModel):
    device_id: str
    batch_id: str
    records: list[dict]


@app.post("/reset")
def reset(req: ResetRequest):
    clinics.clear()
    stock.clear()
    patients.clear()
    visits.clear()
    dispensing_records.clear()
    seen_uuids.clear()
    seen_batches.clear()
    review_queue.clear()
    client_to_server.clear()

    for c in req.clinics:
        clinics[c["id"]] = c
    for s in req.stock:
        stock[s["medicine_id"]] = {"medicine_id": s["medicine_id"], "name": s["name"], "current_stock": s["quantity"]}

    return {"status": "reset", "clinics": len(clinics), "medicines": len(stock)}


def similar_name(a: str, b: str) -> bool:
    a_norm = a.lower().replace(".", " ").split()
    b_norm = b.lower().replace(".", " ").split()
    ratio = SequenceMatcher(None, " ".join(sorted(a_norm)), " ".join(sorted(b_norm))).ratio()
    return ratio > 0.7


def find_possible_duplicate(data: dict) -> Optional[str]:
    for pid, p in patients.items():
        if p.get("nik") == data.get("nik") and data.get("nik") not in ("0000000000000000", "", None):
            return pid
        if p.get("birth_date") == data.get("birth_date") and similar_name(p.get("name", ""), data.get("name", "")):
            return pid
    return None


def process_patient_registration(record: dict, server_time: str) -> dict:
    client_uuid = record["client_uuid"]
    data = record["data"]

    required = ["nik", "name", "birth_date", "gender", "clinic_id"]
    for field in required:
        if field not in data or not data[field]:
            return {"client_uuid": client_uuid, "status": "rejected", "reason": f"missing required field: {field}"}

    server_id = str(uuid.uuid4())
    patient = {
        "id": server_id,
        "client_uuid": client_uuid,
        **data,
        "received_at": server_time,
    }

    existing_id = find_possible_duplicate(data)
    if existing_id:
        patients[server_id] = patient
        client_to_server[client_uuid] = server_id
        review_queue.append({
            "type": "possible_duplicate_patient",
            "new_patient_id": server_id,
            "existing_patient_id": existing_id,
            "reason": "Similar name and birth date",
            "created_at": server_time,
        })
        return {
            "client_uuid": client_uuid,
            "status": "flagged_possible_duplicate_patient",
            "server_id": server_id,
            "existing_patient_id": existing_id,
        }

    patients[server_id] = patient
    client_to_server[client_uuid] = server_id
    return {"client_uuid": client_uuid, "status": "accepted", "server_id": server_id}


def process_visit(record: dict, server_time: str) -> dict:
    client_uuid = record["client_uuid"]
    data = record["data"]

    required = ["patient_client_uuid", "clinic_id", "polyclinic", "visit_date"]
    for field in required:
        if field not in data or not data[field]:
            return {"client_uuid": client_uuid, "status": "rejected", "reason": f"missing required field: {field}"}

    patient_server_id = client_to_server.get(data["patient_client_uuid"])
    if not patient_server_id:
        return {"client_uuid": client_uuid, "status": "rejected", "reason": "patient not found for patient_client_uuid"}

    server_id = str(uuid.uuid4())
    visit = {
        "id": server_id,
        "client_uuid": client_uuid,
        "patient_id": patient_server_id,
        **{k: v for k, v in data.items() if k != "patient_client_uuid"},
        "received_at": server_time,
    }
    visits[server_id] = visit
    client_to_server[client_uuid] = server_id
    return {"client_uuid": client_uuid, "status": "accepted", "server_id": server_id}


def process_dispensing(record: dict, server_time: str) -> dict:
    client_uuid = record["client_uuid"]
    data = record["data"]

    required = ["visit_client_uuid", "medicine_id", "quantity"]
    for field in required:
        if field not in data:
            return {"client_uuid": client_uuid, "status": "rejected", "reason": f"missing required field: {field}"}

    visit_server_id = client_to_server.get(data["visit_client_uuid"])
    if not visit_server_id:
        return {"client_uuid": client_uuid, "status": "rejected", "reason": "visit not found for visit_client_uuid"}

    med_id = data["medicine_id"]
    if med_id not in stock:
        return {"client_uuid": client_uuid, "status": "rejected", "reason": f"unknown medicine: {med_id}"}

    qty = data["quantity"]
    stock[med_id]["current_stock"] -= qty

    if stock[med_id]["current_stock"] < 0:
        review_queue.append({
            "type": "negative_stock",
            "medicine_id": med_id,
            "current_stock": stock[med_id]["current_stock"],
            "created_at": server_time,
        })

    server_id = str(uuid.uuid4())
    dispensing_records[server_id] = {
        "id": server_id,
        "client_uuid": client_uuid,
        "visit_id": visit_server_id,
        "medicine_id": med_id,
        "quantity": qty,
        "received_at": server_time,
    }
    client_to_server[client_uuid] = server_id
    return {"client_uuid": client_uuid, "status": "accepted", "server_id": server_id}


PROCESSORS = {
    "patient_registration": process_patient_registration,
    "visit": process_visit,
    "dispensing": process_dispensing,
}


@app.post("/sync")
def sync(req: SyncRequest):
    server_time = datetime.now(timezone.utc).isoformat()

    if req.batch_id in seen_batches:
        return seen_batches[req.batch_id]

    results = []
    affected_meds = set()

    for record in req.records:
        client_uuid = record.get("client_uuid")
        if not client_uuid:
            results.append({"client_uuid": None, "status": "rejected", "reason": "missing client_uuid"})
            continue

        if client_uuid in seen_uuids:
            results.append({"client_uuid": client_uuid, "status": "duplicate"})
            continue

        schema_version = record.get("schema_version")
        if schema_version is not None and schema_version != 1:
            if schema_version > 1:
                results.append({"client_uuid": client_uuid, "status": "rejected",
                                "reason": "unsupported schema_version"})
                seen_uuids[client_uuid] = {"status": "rejected"}
                continue
            # schema_version 0 or < 1: accept with best effort (same fields)

        record_type = record.get("type")
        processor = PROCESSORS.get(record_type)
        if not processor:
            results.append({"client_uuid": client_uuid, "status": "rejected",
                            "reason": f"unknown record type: {record_type}"})
            seen_uuids[client_uuid] = {"status": "rejected"}
            continue

        result = processor(record, server_time)
        results.append(result)
        seen_uuids[client_uuid] = result

        if record_type == "dispensing" and result["status"] == "accepted":
            affected_meds.add(record["data"]["medicine_id"])

    stock_updates = [
        {"medicine_id": mid, "current_stock": stock[mid]["current_stock"]}
        for mid in affected_meds if mid in stock
    ]

    response = {
        "batch_id": req.batch_id,
        "server_received_at": server_time,
        "results": results,
        "stock_updates": stock_updates,
    }

    seen_batches[req.batch_id] = response
    return response


@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    if patient_id not in patients:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patients[patient_id]


@app.get("/stock/{medicine_id}")
def get_stock(medicine_id: str):
    if medicine_id not in stock:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return stock[medicine_id]


@app.get("/review-queue")
def get_review_queue():
    return {"items": review_queue}
