# Duplicate Registrations

At a Puskesmas (community health clinic), patients register at a front desk. Sometimes the system records the same patient twice within a few minutes - for example, a staff member clicks "register" twice, or two devices register the same walk-in.

## Problem

Given a list of registrations, return the **registration IDs that are duplicates**.

A registration is a **duplicate** if another registration exists for the **same patient** at the **same Puskesmas** within **5 minutes** (inclusive).

When duplicates are found, **keep the earliest** registration and mark the later ones as duplicates.

Each registration has:
- `registration_id` (string)
- `patient_id` (string or null)
- `puskesmas_id` (string)
- `registered_at` (ISO 8601 string with timezone offset, e.g. `"2026-03-15T10:03:00+08:00"`)

If `patient_id` is null, that registration is **never** a duplicate (we can't match it to anyone).

## Example

Input:
```json
[
  {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
  {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:03:00+08:00"},
  {"registration_id": "R3", "patient_id": "P100", "puskesmas_id": "PKM-002", "registered_at": "2026-03-15T10:01:00+08:00"},
  {"registration_id": "R4", "patient_id": null,   "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:01:00+08:00"}
]
```

Output:
```json
["R2"]
```

- R2 is a duplicate of R1 (same patient P100, same Puskesmas PKM-001, 3 minutes apart).
- R3 is NOT a duplicate - different Puskesmas.
- R4 is NOT a duplicate - patient_id is null.

## Your Task

Write a function that takes a list of registrations and returns the list of duplicate registration IDs.
