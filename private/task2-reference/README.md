# Task 2 Reference — Offline-First Sync

Contains reference implementation, design answer key, and language-agnostic grading harness.

## Directory Structure

```
task2-reference/
├── app.py                ← Reference FastAPI sync endpoint (~200 lines)
├── requirements.txt
├── Makefile              ← make run, make grade URL=...
├── design-answer-key.md  ← Strong/acceptable/weak for 7 design questions
└── harness/              ← Grading harness (pytest + httpx)
    ├── conftest.py       ← BASE_URL configuration
    ├── requirements.txt
    ├── test_idempotency.py
    ├── test_partial_invalid.py
    ├── test_duplicate_patient.py
    ├── test_stock_conflict.py
    ├── test_wrong_clock.py
    └── test_old_schema.py
```

## Reference Implementation

`app.py` implements:
- **Idempotency**: Dedup by `client_uuid` (record-level) and `batch_id` (batch-level)
- **Duplicate patients**: Fuzzy name match → flag for human review (never auto-merge)
- **Stock policy**: Always allow dispensing, negative stock triggers review queue flag
- **Endpoints**: POST /sync, GET /patients/{id}, GET /stock/{id}, GET /review-queue, POST /reset

## Running Reference Server

```bash
cd private/task2-reference/

# Setup (one-time)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r harness/requirements.txt

# Start server
.venv/bin/uvicorn app:app --port 8000
# or: make run
```

## Running Grading Harness

Harness is **language-agnostic** — hits any HTTP server implementing the API contract.

```bash
# Against reference (self-test)
make grade URL=http://localhost:8000

# Against candidate's endpoint
make grade URL=http://localhost:<candidate-port>

# If candidate runs in Docker
make grade URL=http://host.docker.internal:<port>

# Or directly
.venv/bin/python -m pytest harness/ -v --tb=short --base-url=http://localhost:8000
```

### Test Coverage (14 tests)

| Test File | What It Tests |
|-----------|--------------|
| `test_idempotency.py` | Record-level + batch-level dedup, replay safety |
| `test_partial_invalid.py` | Mixed valid/invalid records in one batch, per-record status |
| `test_duplicate_patient.py` | Same patient from different devices, placeholder NIK handling |
| `test_stock_conflict.py` | Dispensing beyond stock, negative stock handling |
| `test_wrong_clock.py` | Future timestamps, device clock drift |
| `test_old_schema.py` | Payload from older schema version |

### Interpreting Results

X/14 pass → feeds into "Endpoint + Tests" criterion (25 points in rubric).

- **12+/14**: Strong
- **8-11/14**: Acceptable
- **<8/14**: Weak

## Evaluating Design Doc

Open `design-answer-key.md`. For each of 7 design questions, compare candidate's answer:

1. **Exactly-once delivery** — client UUID + server dedup? Or vague "use a queue"?
2. **Duplicate patients** — flag for review? Or auto-merge by name?
3. **Stock policy** — always dispense? Or reject on insufficient?
4. **Clock drift** — server timestamp? Or trust device?
5. **Lost device** — PII risk addressed?
6. **Schema migration** — versioning strategy?
7. **MVP scope** — pragmatic? Or CRDTs for a 2-month project?

### Red Flags (likely AI-generated, not understood)

- Auto-merge patients by Levenshtein distance
- Reject dispensing when stock insufficient
- Trust device clock for ordering
- CRDTs or event sourcing for MVP
