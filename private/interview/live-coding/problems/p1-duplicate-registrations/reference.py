from datetime import datetime, timedelta


def find_duplicates(registrations: list[dict]) -> list[str]:
    """Return registration IDs that are duplicates.

    A registration is a duplicate if the same patient registered at the
    same puskesmas within 5 minutes (inclusive) of a kept registration.
    Keep the earliest; mark later ones as duplicates.
    Null patient_id is never a duplicate.
    """
    valid = [r for r in registrations if r["patient_id"] is not None]

    for r in valid:
        r["_ts"] = datetime.fromisoformat(r["registered_at"])

    valid.sort(key=lambda r: (r["patient_id"], r["puskesmas_id"], r["_ts"]))

    duplicates = []
    last_kept = {}

    for r in valid:
        key = (r["patient_id"], r["puskesmas_id"])
        ts = r["_ts"]

        if key in last_kept and (ts - last_kept[key]) <= timedelta(minutes=5):
            duplicates.append(r["registration_id"])
        else:
            last_kept[key] = ts

    return duplicates
