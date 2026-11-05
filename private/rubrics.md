# Scoring Rubrics

## Final Weighting

| Component | Weight |
|-----------|--------|
| Task 1 (required) | 35% |
| Chosen task (Task 2 or Task 3) | 35% |
| Take-home walkthrough (follow-up call) | 15% |
| Live coding session (follow-up call) | 15% |

Both optional tasks scored out of 100. Candidates who chose differently are compared directly. No extra points for completing a third task.

---

## Task 1: Clinic Sync Service Review (100 points)

### Prioritization (30 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 25-30 | Data-loss and safety issues (D1, D4, D3) ranked above style/operational issues. Clear reasoning for ranking order. Acknowledges that multiple orderings are defensible and explains their choice. |
| Acceptable | 15-24 | Mostly correct prioritization. May rank a style issue too high or miss one critical defect. Reasoning present but not fully developed. |
| Weak | 0-14 | Style issues (naming, code structure) ranked above data corruption. No clear priority framework. Finds issues but cannot differentiate severity. |

**AI-default red flags:** Style/formatting issues ranked in top 3. Generic severity labels ("high/medium/low") without context. Lists that read like an automated scan output.

### Impact Analysis per Stakeholder (20 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 16-20 | Names specific stakeholders (patient, clinic staff, finance, Dinkes) and explains exactly what goes wrong for each. "Finance must manually reconcile phantom claims across 40 clinics" > "could cause financial issues." |
| Acceptable | 10-15 | Names stakeholders and describes impact but stays generic. "Patients could get wrong medication." |
| Weak | 0-9 | No stakeholder analysis. Generic statements like "this is a bug" or "this could cause problems." |

### Fixes + Tests (30 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 25-30 | Fixes the 3 most impactful defects. Each fix has a test that fails before and passes after. Tests exercise the actual failure mode, not just happy path. Code is clean and minimal. |
| Acceptable | 15-24 | Fixes 3 issues (may not be the top 3). Tests exist but may not fully exercise the failure mode. Some over-engineering in fixes. |
| Weak | 0-14 | Fixes easy issues (D2, D10) instead of impactful ones (D1, D4). Tests only check happy path. Fix introduces new bugs. |

### "Not Fixed" Reasoning (10 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 8-10 | Lists remaining issues with clear reasoning: "D8 is important but won't cause data loss before go-live with 40 clinics. I'd fix it in the next sprint." Time-boxed decision making. |
| Acceptable | 5-7 | Lists issues not fixed but reasoning is brief or generic. |
| Weak | 0-4 | No list, or "I didn't have time" without analysis. |

### Code Clarity (10 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 8-10 | Fixes are minimal and surgical. Existing tests still pass. Code matches the existing style. No unnecessary refactoring. |
| Acceptable | 5-7 | Fixes work but touch more code than necessary. Minor style inconsistencies. |
| Weak | 0-4 | Rewrites large sections. Breaks existing tests. Introduces new abstractions. |

---

## Task 2: Offline-First Sync (100 points)

### Exactly-Once Delivery (25 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 20-25 | Client UUID + server dedup. Batch-level idempotency. Acknowledges "exactly once = at least once + idempotent." Addresses the ack problem. |
| Acceptable | 12-19 | Client UUID dedup. May miss batch idempotency or ack problem. |
| Weak | 0-11 | No concrete mechanism. "Use a queue." Relies on network reliability. |

### Duplicate-Patient Policy (15 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 12-15 | Flag for human review. Explains why auto-merge is dangerous. Handles placeholder NIK as special case. |
| Acceptable | 7-11 | Flag and queue but doesn't address placeholder NIK. |
| Weak | 0-6 | Auto-merge by name similarity. No human review. |

**AI-default red flag:** "Use fuzzy matching with Levenshtein distance to auto-merge patients."

### Clinic-Appropriate Stock Policy (10 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 8-10 | Always allow dispensing. Negative stock + reconciliation flag. Understands that a clinic cannot refuse medicine because of a data sync issue. |
| Acceptable | 5-7 | Allows dispensing but doesn't explain the clinical reasoning. |
| Weak | 0-4 | Rejects dispensing when stock is insufficient. |

**AI-default red flag:** "Reject the transaction and alert the user" — shows no understanding of the clinical context.

### Clock / Lost Device / Schema Migration (15 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 12-15 | Server timestamp for ordering. PII risk for lost devices with encryption proposal. Schema versioning with backward compatibility. All three addressed practically. |
| Acceptable | 7-11 | Addresses all three but some are surface-level. |
| Weak | 0-6 | Misses one or more. Trusts device clock. No PII concern. |

### Scope Discipline (10 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 8-10 | Clear MVP vs. later. Explains why specific things are deferred. No over-engineering. |
| Acceptable | 5-7 | Lists deferrals but reasoning is thin. |
| Weak | 0-4 | Proposes CRDTs, event sourcing, or distributed locks for a 2-month MVP. |

### Endpoint + Tests — Harness Score (25 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 20-25 | Harness passes 12+/14. Clean endpoint starts with one command. Well-structured code. |
| Acceptable | 12-19 | Harness passes 8-11/14. Endpoint works but may have rough edges. |
| Weak | 0-11 | Harness passes <8/14. Endpoint doesn't start cleanly or fails basic scenarios. |

---

## Task 3: Dinkes Report (100 points)

### Problems Found (30 points) — expect ≥6 of 9

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 24-30 | Finds 7+ of 9 anomalies. Names them specifically with evidence (row counts, example IDs). Groups related issues (A3+A4+A5 are all patient identity problems). |
| Acceptable | 15-23 | Finds 5-6 anomalies. May miss subtler ones (A5, A7, A9). Evidence present but incomplete. |
| Weak | 0-14 | Finds ≤4 anomalies. Generic observations ("data has some inconsistencies"). |

**AI-default red flag:** "I found several data quality issues including missing values, duplicates, and outliers" — vague, no specifics.

### Handling Decisions (25 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 20-25 | Each anomaly has a stated decision with reasoning. "I excluded cancelled registrations because a no-show is not a visit. This reduced the count by ~680 rows." Acknowledges where different decisions are defensible. |
| Acceptable | 12-19 | Decisions present but reasoning is brief. Some anomalies handled without explanation. |
| Weak | 0-11 | No decisions stated. Query just runs against raw data. |

### Clarifying Question Quality (15 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 12-15 | Question that would change the answer: "Does a multi-polyclinic visit count as 1 or 2?" or "Should PKM-002-OLD and PKM-002 be merged?" Specific and actionable. |
| Acceptable | 7-11 | Reasonable question but doesn't change the core result. Or good question phrased vaguely. |
| Weak | 0-6 | No question, or "Is the data clean?" or format questions. |

**AI-default red flag:** A question that reveals AI-generated but not understood anomaly list.

### Numbers Correct Under Stated Assumptions (20 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 16-20 | Numbers match ground truth for their stated interpretation. If they chose Interpretation 1, their totals are within 2% of our Interpretation 1 numbers. Shows their work (SQL or code). |
| Acceptable | 10-15 | Numbers are close but have minor errors. SQL is reasonable but misses an edge case. |
| Weak | 0-9 | Numbers match the naive result exactly (no cleaning). Or numbers are far off with no explanation. |

**AI-default red flag:** `COUNT(DISTINCT nik)` with no caveat about placeholder NIKs.

### SQL Readability (10 points)

| Level | Points | Description |
|-------|--------|-------------|
| Strong | 8-10 | CTEs with clear names. Comments explain non-obvious decisions. Reproducible. |
| Acceptable | 5-7 | Readable but could be cleaner. Works correctly. |
| Weak | 0-4 | Unreadable, or Python script that can't be easily verified. |

---

## Take-Home Walkthrough (15% of final)

Scored holistically, not per-question. Signals:

| Signal | Strong | Weak |
|--------|--------|------|
| Code ownership | Explains any line, knows trade-offs | Can't explain their own code |
| Adaptability | Handles live changes smoothly | Freezes or restarts from scratch |
| Depth | Answers follow-ups without prompting | Only surface-level answers |
| Honesty | "I didn't know X, so I looked it up" | Pretends to know everything |
| AI awareness | "AI suggested X but I changed it because Y" | Can't identify what AI contributed |

---

## Live Coding Session (15% of final)

30 minutes, one problem, no AI tools. See `interview/live-coding/scoring-sheet.md` for detailed scoring.

| Area | Weight (within this 15%) |
|------|--------------------------|
| Clarifying questions | 15% |
| Approach before coding | 15% |
| Correctness | 25% |
| Edge cases | 20% |
| Testing own code | 10% |
| Communication | 10% |
| Twist response | 5% |

Hints reduce the score (see scoring sheet for specifics). A candidate who reasons well but doesn't finish can still meet expectations.
