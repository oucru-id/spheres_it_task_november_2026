# Task 1 Answer Key — Clinic Sync Service

Contains defect catalog, clean reference implementation, and automated detection tests.

## Directory Structure

```
task1-answer-key/
├── defects.md           ← D1-D10 catalog with severity, location, stakeholder impact
├── reference-fixes/     ← Clean version of candidate code (all 10 defects fixed)
│   ├── app.py           ← Main service: Decimal money, atomic stock, token refresh, etc.
│   ├── config.py
│   ├── database.py      ← INTEGER for money amounts (not REAL)
│   ├── models.py        ← amount: int (not float)
│   └── mock_claim_api.py
└── detection-tests/     ← 1 pytest per defect
    ├── conftest.py      ← Shared fixtures, sys.path config
    └── test_d01..d10_*.py
```

## Defect Summary (D1-D10)

| # | Defect | Severity | File:Line |
|---|--------|----------|-----------|
| D1 | No idempotency on claim retry | Critical | app.py: submit_claim_to_api() |
| D2 | Float money (REAL in SQLite) | High | database.py, models.py, app.py |
| D3 | Stock race condition (read-modify-write) | High | app.py: dispense_medicine() |
| D4 | Swallowed errors (try/except + unconditional synced=1) | Critical | app.py: sync_pending_claims() |
| D5 | NIK-only patient match (misses placeholder NIKs) | High | app.py: get_or_create_patient() |
| D6 | Naive timestamps (datetime.now(), no timezone) | Medium | app.py: throughout |
| D7 | Token cached forever (module-level, never refreshed) | Medium | app.py: _token |
| D8 | Unbounded query (no LIMIT on synced=0) | Medium | app.py: sync_pending_claims() |
| D9 | No backoff, 429 ignored (fixed sleep(1)) | Low | app.py: submit_claim_to_api() |
| D10 | PII in logs (NIK, name, diagnosis) | High | app.py: logger.info() calls |

Full details in `defects.md`.

## Running Detection Tests

```bash
cd private/task1-answer-key/detection-tests/

# Setup (one-time)
python3 -m venv .venv
.venv/bin/pip install fastapi uvicorn httpx pydantic pytest

# Point to candidate's code
# Edit conftest.py: change sys.path.insert to candidate's task1 directory

# Run all detection tests
.venv/bin/python -m pytest -v --tb=short
```

### Interpreting Results

- **Test FAILS** = defect still present (candidate didn't fix it)
- **Test PASSES** = defect was fixed

Cross-reference with candidate's REVIEW.md:
1. Did they **find** it? (listed in their review)
2. Did they **rank** it correctly? (compare with severity tiers above)
3. Did they **fix** the right ones? (top 3 by impact, not top 3 by ease)

## Reference Fixes

`reference-fixes/` contains the clean implementation. Key differences from candidate code:

- **D1 fix**: Check `external_claim_id` before re-posting; use claim_reference for dedup
- **D2 fix**: INTEGER storage (cents), `amount: int` in Pydantic models
- **D3 fix**: Atomic `UPDATE ... SET stock = stock - ? WHERE stock >= ?`
- **D4 fix**: Only set `synced=1` inside try block, after confirmed success
- **D5 fix**: Match on `nik + name + birth_date`, skip placeholder NIKs
- **D6 fix**: `datetime.now(timezone.utc)` everywhere
- **D7 fix**: Token expiry tracking, refresh before use
- **D8 fix**: `LIMIT 100` on pending claims query
- **D9 fix**: Exponential backoff, respect `Retry-After` header on 429
- **D10 fix**: Hash/mask PII in log output
