# Task 1: Defect Catalog

## Expected Severity Ranking

**Tier 1 — Data corruption / loss (must-fix before go-live):**
1. **D1** — Duplicate claim submission (financial loss)
2. **D4** — Swallowed errors mark failed claims as synced (silent data loss)
3. **D3** — Medicine stock race condition (patient safety)
4. **D10** — PII/health data in logs (compliance violation)

**Tier 2 — Correctness issues (high priority):**
5. **D5** — Patient matching by NIK only (record merging)
6. **D2** — Money as float (financial rounding errors)
7. **D6** — Naive timestamps (cross-timezone data corruption)

**Tier 3 — Operational issues (important but not data-corrupting):**
8. **D7** — Token cached without expiry (service outage after token expires)
9. **D8** — Unbounded query (memory/performance at scale)
10. **D9** — No backoff, 429 ignored (API ban, cascading failures)

---

## Detailed Defect Descriptions

### D1: No Idempotency on Claim Submission Retry

**File:** `app.py`, `submit_claim_to_api()` (line ~140)
**Code:** Retry loop re-POSTs the claim with no `claim_reference` or deduplication check. The mock API does not deduplicate — each POST creates a new claim.
**Impact:** After a timeout + retry, duplicate claims appear in the insurance system. Finance must manually reconcile. At 40 clinics with ~5% timeout rate, this creates dozens of phantom claims per day.
**Who notices:** Finance team during reconciliation. Potentially BPJS auditors.

### D2: Money as Float

**File:** `database.py` (bills/claims columns: `REAL`), `models.py` (`BillRecord.amount: float`)
**Code:** Amounts stored as `REAL` in SQLite and `float` in Python. Summed with `sum()`.
**Impact:** Floating-point rounding errors accumulate. A bill of 150,000.10 IDR may become 150,000.09999... Individual errors are small but aggregate across thousands of transactions. Monthly totals won't match to the cent.
**Who notices:** Finance during monthly reconciliation. Auditors comparing claim totals.

### D3: Medicine Stock Race Condition

**File:** `app.py`, `dispense_medicine()` (line ~95)
**Code:** Reads current stock, subtracts in Python, writes back. No transaction, lock, or atomic update.
**Impact:** Under concurrent requests (multiple clinics syncing simultaneously), two dispensing operations read the same stock value and both write back, losing one decrement. Stock can also go negative with no check.
**Who notices:** Pharmacy staff during stock counting. Patients if medicine is dispensed that doesn't exist.

### D4: Swallowed Errors

**File:** `app.py`, `sync_pending_claims()` (line ~160)
**Code:** `try/except Exception: logger.warning(...)` around claim submission, then unconditionally `UPDATE claims SET synced = 1`.
**Impact:** A failed or timed-out claim is marked as synced. The claim is never retried and silently lost. The insurance never receives it, but the system thinks it did.
**Who notices:** Nobody — until a patient's claim is rejected or a clinic's monthly total doesn't match.

### D5: Patient Matching by NIK Only

**File:** `app.py`, `get_or_create_patient()` (line ~43)
**Code:** `SELECT id FROM patients WHERE nik = ?` — matches on NIK alone.
**Impact:** Placeholder NIK `0000000000000000` (used for patients without ID) causes all such patients to merge into one record. Infants registered under the mother's NIK are merged with the mother. Different people become one patient.
**Who notices:** Clinic staff seeing wrong patient history. Doctors seeing mixed diagnoses. Dinkes with incorrect patient counts.

### D6: Naive Timestamps

**File:** `app.py`, throughout — `datetime.now()` (no timezone)
**Code:** All timestamps use `datetime.now()` (naive, local time). Visit timestamps from clinics in WITA (UTC+8) and WIB (UTC+7) are stored and compared without timezone context.
**Impact:** Visits near midnight are assigned to the wrong date. Monthly and daily reports are incorrect for cross-timezone comparisons. A visit at 23:30 WIB appears as a different date than a simultaneous visit at 00:30 WITA.
**Who notices:** Dinkes when cross-facility reports show inconsistent dates. Finance when daily billing totals don't match.

### D7: Token Cached Without Expiry

**File:** `app.py`, `get_token()` (line ~29)
**Code:** Token fetched once and stored in `_token`. Never refreshed, even after expiry.
**Impact:** After the token expires (default 1 hour), all claim submissions fail with 401. Since errors are swallowed (D4), claims silently stop syncing.
**Who notices:** Nobody immediately (due to D4). Eventually finance notices missing claims.

### D8: Unbounded Query

**File:** `app.py`, `sync_pending_claims()` (line ~155)
**Code:** `SELECT * FROM claims WHERE synced = 0` with no `LIMIT`.
**Impact:** If sync falls behind (network outage, D7 token expiry), thousands of unsynced claims load into memory at once. Can OOM the service or create a very long sync cycle.
**Who notices:** Ops team when the service crashes or becomes unresponsive after a backlog builds up.

### D9: No Backoff, 429 Ignored

**File:** `app.py`, `submit_claim_to_api()` (line ~140)
**Code:** Fixed `time.sleep(1)` retry on any error, including HTTP 429. No exponential backoff, no `Retry-After` header handling.
**Impact:** When rate-limited, the service hammers the API with retries every second, making the rate limit worse. Could get the API key banned. Combined with D8 (unbounded batch), creates a thundering herd.
**Who notices:** Claim API provider. Ops team when syncing fails repeatedly.

### D10: PII/Health Data in Logs

**File:** `app.py`, multiple `logger.info()` calls
**Code:** Logs include patient NIK, name, and diagnosis on every operation.
**Impact:** Log files contain protected health information (PHI). Any log aggregation, debugging session, or log file access exposes patient data. Violates Indonesian data protection regulations (UU PDP) and health data confidentiality requirements.
**Who notices:** Security auditor. Data protection officer. Regulators if there's a breach.

---

## Why Style Issues Should Rank Low

Candidates who rank style issues (inconsistent naming, missing type hints, long functions) above data corruption, financial loss, or compliance violations are demonstrating a lack of production experience. Style issues cause maintenance friction; the defects above cause real harm to real people.
