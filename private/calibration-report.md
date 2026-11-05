# Calibration Report

## 1. Test Verification

### Task 1: Happy-Path Tests
- **Result:** 11/11 pass on candidate (buggy) code
- **Verified:** Tests carefully avoid all 10 defect triggers (single timezone, no concurrency, no placeholder NIKs, small batches, fresh token)

### Task 1: Detection Tests
- **Status:** 10 detection tests created (one per defect)
- **Expected:** All fail on candidate code, all pass on reference code
- **Note:** Detection tests use source inspection (D8, D9) and behavioral checks (D1-D7, D10)

### Task 2: Grading Harness
- **Result:** 14/14 pass against reference implementation
- **Scenarios covered:** idempotency (batch + record), partial invalid, duplicate patients, stock conflict, wrong clock, old schema version

## 2. Naive-Solve Check

### Task 1: AI Review Simulation
A naive AI review of `app.py` would likely catch:
- **Easily found:** D10 (PII in logs — obvious `logger.info` with patient data), D2 (float money — `REAL` in schema), D8 (unbounded query — no LIMIT visible), D7 (token caching — clear singleton pattern)
- **Probably found:** D6 (naive timestamps — `datetime.now()` without timezone), D9 (no backoff — fixed `sleep(1)`)
- **Harder to find:** D1 (no idempotency — requires understanding the mock API behavior), D3 (stock race — looks procedurally correct), D4 (swallowed errors — the `try/except` + unconditional `synced=1` requires careful reading), D5 (NIK-only matching — requires domain knowledge about placeholder NIKs)

**Assessment:** A naive AI review would likely find 6-7 of 10 defects but would struggle with **prioritization and impact analysis**. It would likely rank D10 and D2 highly (common AI patterns) while missing that D1 and D4 cause actual data loss. The differentiation is in the ranking and real-world impact reasoning, not in finding the defects.

### Task 3: Naive Query
```sql
SELECT clinic_id, substr(visit_date, 1, 7) as month,
       COUNT(*) as visits, COUNT(DISTINCT nik) as patients
FROM visits v JOIN patients p ON v.patient_id = p.id
GROUP BY clinic_id, month
```
**Missed anomalies:**
- A1 (multi-polyclinic): counted as multiple visits ✓ (but candidate should question interpretation)
- A2 (cancelled registrations): included in count ✗
- A3 (placeholder NIK): collapses ~303 people into 1 ✗
- A4 (name variants): not detected ✗
- A5 (infant under mother NIK): merged with mother ✗
- A6 (retry duplicates): counted twice ✗
- A7 (mixed timestamps): wrong month for some visits ✗
- A8 (implausible records): included ✗
- A9 (facility renamed): shows as two separate facilities ✗

**Assessment:** Naive query catches 0 of 9 anomalies. The naive result table will show "PKM-002-OLD" as a separate facility and significantly different patient counts, which is a strong discriminator.

## 3. Leak Check

Grep of `candidate/` for hint words: **clean.** No matches for: bug, race, unsafe, anomaly, planted, TODO, FIXME, HACK, defect.
No generator scripts, answer keys, reference solutions, rubrics, or detection tests in `candidate/`.

## 4. Time Sanity Check

| Task | Estimated Time (mid-level engineer) |
|------|-------------------------------------|
| Task 1: Read code, identify issues, rank, fix top 3, write tests | ~5 hours |
| Task 2: Design doc (7 questions) + implement sync endpoint + tests | ~6 hours |
| Task 3: Explore data, find anomalies, write query, document assumptions | ~5 hours |

**Combination A (Task 1 + Task 2):** ~11 hours — at upper bound
**Combination B (Task 1 + Task 3):** ~10 hours — comfortable

**Assessment:** Both combinations within the 10-11 hour target. Task 2 is intentionally 1 hour longer to account for the design document; this is balanced by Task 2 being more open-ended (no single correct answer for design questions).

## 5. Setup Check

### Task 1 Docker Path
- `docker compose up --build`: builds two services, starts on ports 8000/8001
- Health checks: `curl localhost:8000/health` and `curl localhost:8001/health`
- Tests: `docker compose run --rm clinic-sync pytest tests/ -v`
- Reset: `docker compose run --rm clinic-sync rm -f data/clinic.db && docker compose restart`
- **Verified:** SETUP.md matches actual commands

### Task 1 Non-Docker Path
- `make setup`: creates venv, installs deps
- `make run`: starts both services
- `make test`: runs pytest
- `make reset-db`: removes SQLite file
- **Verified:** All 11 tests pass

### Task 2
- Sample sender scripts (`send-samples.sh`, `send_samples.py`): verified against reference
- **Verified:** Both scripts execute correctly against reference endpoint

### Task 3
- `sqlite3 clinic_data.sqlite ".tables"`: shows all 5 tables
- **Verified:** File opens with standard tools, schema matches SCHEMA.md

## 6. Balance Check

| Dimension | Task 2 | Task 3 |
|-----------|--------|--------|
| Time | ~6h | ~5h |
| Skill tested | System design + backend implementation | Data analysis + SQL |
| Ambiguity | High (design decisions) | High (data quality interpretation) |
| AI vulnerability | Design reasoning hard to fake | Anomaly discovery + judgment hard to fake |
| Output volume | ~3 page design + ~200 line endpoint + tests | ~50 line query + ~2 page assumptions |

**Assessment:** Balanced. Neither is the obvious "easy pick." Task 2 requires more code but has more degrees of freedom. Task 3 requires less code but demands careful data exploration and stated assumptions.
