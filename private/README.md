# SPHERES Take-Home Assessment — Evaluator Guide

> **This directory is private.** Nothing here should be shared with candidates. The `candidate/` directory (one level up) is what candidates receive.

## Quick Start for Evaluators

### 1. Understand the Assessment Structure

Candidates complete **Task 1 (required)** + their choice of **Task 2 or Task 3**.

| Task | What Candidate Does | How You Grade |
|------|--------------------|----|
| Task 1 — Clinic Sync | Review a buggy FastAPI service, rank issues, fix top 3 | Run detection tests against their fixes |
| Task 2 — Offline Sync | Design doc + implement a sync endpoint | Run grading harness against their endpoint |
| Task 3 — Dinkes Report | Write SQL against messy SQLite data | Compare numbers to ground truth |

Final score: **Task 1 (35%) + Chosen Task (35%) + Follow-up Call (30%)**

### 2. Prerequisites

- Python 3.11+ (for running tests and reference implementations)
- Docker (optional, for Task 1 Docker path verification)
- An SQLite client (for Task 3 spot-checks)

### 3. One-Time Setup

```bash
# Task 1 detection tests
cd private/task1-answer-key/detection-tests/
python3 -m venv .venv
.venv/bin/pip install fastapi uvicorn httpx pydantic pytest

# Task 2 grading harness
cd private/task2-reference/
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r harness/requirements.txt
```

---

## Directory Map

```
private/
├── README.md                ← You are here
├── HOW_TO_GRADE.md          ← Step-by-step grading workflow
├── rubrics.md               ← Scoring rubrics (strong/acceptable/weak per criterion)
├── interview-guide.md       ← 45-minute follow-up call script with note-taking space
├── calibration-report.md    ← Test results, naive-solve analysis, balance check
│
├── generators/              ← Data generators (seeded, deterministic)
│   ├── base.py              ← Shared: Faker (id_ID), NIK generator, clinic data
│   ├── task3_data_generator.py  ← Generates clinic_data.sqlite with anomalies A1-A9
│   └── requirements.txt
│
├── task1-answer-key/
│   ├── defects.md           ← D1-D10 catalog: location, impact, severity ranking
│   ├── reference-fixes/     ← Clean version of the service (all 10 defects fixed)
│   │   ├── app.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── mock_claim_api.py
│   └── detection-tests/     ← 1 pytest per defect (fails on buggy, passes on clean)
│       ├── conftest.py
│       └── test_d01..test_d10_*.py
│
├── task2-reference/
│   ├── app.py               ← Reference FastAPI sync endpoint
│   ├── requirements.txt
│   ├── Makefile              ← `make run`, `make grade URL=...`
│   ├── design-answer-key.md  ← Strong/acceptable/weak for each design question
│   └── harness/             ← Language-agnostic grading harness (pytest + httpx)
│       ├── conftest.py
│       ├── test_idempotency.py
│       ├── test_partial_invalid.py
│       ├── test_duplicate_patient.py
│       ├── test_stock_conflict.py
│       ├── test_wrong_clock.py
│       ├── test_old_schema.py
│       └── requirements.txt
│
└── task3-answer-key/
    ├── anomalies.md          ← A1-A9 with exact counts, example IDs, detection SQL
    ├── ground-truth.md       ← Correct numbers under 3 interpretations
    ├── reference-solution.sql ← SQL for Interpretation 1 (recommended)
    ├── good-clarifying-questions.md  ← What strong/weak questions look like
    └── generation_stats.json  ← Raw stats from data generator
```

---

## How to Evaluate Each Task

### Task 1: Clinic Sync Service

**What to read from the candidate:**
- `task1/REVIEW.md` — their issue list and ranking
- Their code fixes (diff against the original `candidate/task1-clinic-sync/app.py`)
- Their fix tests

**How to run detection tests:**

```bash
cd private/task1-answer-key/detection-tests/

# Edit conftest.py line 7: point sys.path to the candidate's task1 directory
# e.g., sys.path.insert(0, "/path/to/candidate-submission/task1")

.venv/bin/python -m pytest -v --tb=short
```

Each failing test = a defect they **did not** fix. Each passing test = a defect they **did** fix. Cross-reference with their REVIEW.md to check:

- Did they find it? (listed in REVIEW.md)
- Did they rank it correctly? (compare with `defects.md` severity tiers)
- Did they fix the right ones? (top 3 by impact, not top 3 by ease)

**Key scoring signals:**
- D1 (duplicate claims) and D4 (swallowed errors) are the most impactful — fixing these shows production instinct
- D2 (float money) and D10 (PII) are easiest to find — if they only fix these, it's a weak signal
- See `rubrics.md` for detailed scoring

### Task 2: Offline-First Sync

**What to read from the candidate:**
- `task2/DESIGN.md` — their design document (max 3 pages)
- Their endpoint code
- Their tests

**How to run the grading harness:**

```bash
# Start the candidate's endpoint on port 8000 (follow their README instructions)

cd private/task2-reference/

# Grade against their running endpoint
.venv/bin/python -m pytest harness/ -v --tb=short
# or:
make grade URL=http://localhost:8000

# If their server runs in Docker:
make grade URL=http://host.docker.internal:8000
```

**Result:** X/14 tests pass. This feeds directly into the "Endpoint + Tests" criterion (25 points).

**For the design doc:** Compare each of the 7 sections against `design-answer-key.md`. Key red flags:
- Auto-merging patients by name similarity
- Rejecting dispensing when stock is insufficient
- Trusting the device clock for ordering
- CRDTs or event sourcing for a 2-month MVP

### Task 3: Dinkes Report

**What to read from the candidate:**
- Their SQL/script
- Their result table
- `task3/ASSUMPTIONS.md`
- Their clarifying question (if sent)

**How to evaluate:**

1. Open `ground-truth.md` and determine which interpretation the candidate used
2. Compare their numbers row by row:
   - If they match **Interpretation 3 (naive)** → they didn't find the anomalies
   - If they match **Interpretation 1** or **2** → check which anomalies they cleaned
3. Count how many of the 9 anomalies they found in ASSUMPTIONS.md (compare with `anomalies.md`)
4. Rate their clarifying question (compare with `good-clarifying-questions.md`)

**Quick check — did they fall for the naive trap?**
- Their PKM-002 data shows two separate facilities (PKM-002 and PKM-002-OLD) → missed A9
- Their patient counts use `COUNT(DISTINCT nik)` → missed A3/A4/A5
- Their visit counts include cancelled registrations → missed A2

---

## How to Run the Follow-Up Call

1. Before the call: review their submission using steps above
2. Open `interview-guide.md` — it has the full 45-minute script
3. The guide has note-taking space built in
4. Key structure:
   - Task 1 questions (~15 min) — prioritization reasoning + code walkthrough
   - Chosen task (~20 min) — live constraints (Task 2) or live query change (Task 3)
   - Skipped task (~5 min) — one light verbal question
   - AI usage (~5 min) — "What did the AI get wrong?"

---

## How to Regenerate Data

If you need to regenerate the Task 3 SQLite file (e.g., after modifying anomaly parameters):

```bash
cd private/generators/
pip install -r requirements.txt
python3 task3_data_generator.py
```

The generator is deterministic (seed=42). Same seed = identical output. The generated file goes directly to `candidate/task3-dinkes-report/clinic_data.sqlite`.

Stats are saved to `private/task3-answer-key/generation_stats.json`. After regenerating, update `ground-truth.md` and `anomalies.md` with new counts.

---

## Key Files for Quick Reference

| When you need... | Open this file |
|-----------------|---------------|
| Step-by-step grading workflow | `HOW_TO_GRADE.md` |
| Scoring criteria and point values | `rubrics.md` |
| Task 1 defect details | `task1-answer-key/defects.md` |
| Task 2 design evaluation | `task2-reference/design-answer-key.md` |
| Task 3 correct numbers | `task3-answer-key/ground-truth.md` |
| Task 3 anomaly details | `task3-answer-key/anomalies.md` |
| Follow-up call script | `interview-guide.md` |
| Calibration and balance analysis | `calibration-report.md` |

---

## Troubleshooting

**Detection tests import error:** Make sure `conftest.py` sys.path points to the candidate's actual task1 directory, not the template.

**Harness can't reach candidate endpoint:** If the candidate's server runs in Docker, use `http://host.docker.internal:<port>` instead of `localhost`.

**Task 3 numbers don't match any interpretation:** The candidate may have used a hybrid approach. Check if their numbers are internally consistent with their stated assumptions — that's what matters.

**Candidate completed all 3 tasks:** Score only Task 1 + their stated choice (from `CHOICE.md`). Do not award extra credit.
