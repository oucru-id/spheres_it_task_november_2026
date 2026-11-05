# SPHERES IT Take-Home Assessment (November 2026)

Take-home assessment for **Mid Fullstack Software Engineer** candidates joining the SPHERES project at OUCRU Indonesia.

## What This Repo Contains

```
spheres_it_task_november_2026/
├── candidate/                  # What candidates receive
│   ├── README.md               # Assessment overview, submission instructions
│   ├── task1-clinic-sync/      # Required: review and fix a FastAPI service
│   ├── task2-offline-sync/     # Optional: design + implement offline sync endpoint
│   └── task3-dinkes-report/    # Optional: SQL report from messy SQLite data
│
├── private/                    # Evaluator-only (never share with candidates)
│   ├── README.md               # Evaluator setup and operation guide
│   ├── HOW_TO_GRADE.md         # Step-by-step grading workflow
│   ├── rubrics.md              # Scoring criteria per task
│   ├── interview-guide.md      # Follow-up call script (if applicable)
│   ├── calibration-report.md   # Test results and balance analysis
│   ├── generators/             # Deterministic data generators (seed=42)
│   ├── task1-answer-key/       # 10 planted defects, reference fixes, detection tests
│   ├── task2-reference/        # Reference implementation + grading harness (14 tests)
│   └── task3-answer-key/       # 9 planted anomalies, ground truth, reference SQL
│
└── DISTRIBUTION.md             # How to send materials to candidates vs interviewers
```

## How the Assessment Works

Candidates complete **Task 1 (required)** plus their choice of **Task 2 or Task 3**. They have 3 days.

| Task | What Candidates Do | What Makes It Hard |
|------|-------------------|-------------------|
| **Task 1** | Review a FastAPI clinic sync service, rank issues, fix top 3 | 10 planted defects (D1-D10) hidden in natural-looking code. Happy-path tests all pass. Differentiation is in prioritization and impact reasoning, not finding bugs. |
| **Task 2** | Write a design doc (7 questions) + implement a sync endpoint | Questions are designed so AI-default answers are wrong (e.g., "reject dispensing on low stock" fails in a clinic context). |
| **Task 3** | Produce monthly patient/visit numbers from SQLite data | 9 planted anomalies (A1-A9) in the data. Naive query gives wrong numbers. Differentiation is in what they notice and how they handle it. |

AI tools are allowed - candidates must document usage in `AI_USAGE.md`.

## What to Do as an Interviewer

### First Time Setup

1. Clone this repo
2. Read `private/README.md` for full setup instructions
3. Set up Python venvs for the grading tools (one-time, ~5 min):
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

### When a Candidate Submits

Follow `private/HOW_TO_GRADE.md` step by step:

1. **Task 1**: Run detection tests against their code - tells you which defects they fixed
2. **Task 2** (if chosen): Run grading harness against their endpoint - gives X/14 score
3. **Task 3** (if chosen): Compare their numbers against `private/task3-answer-key/ground-truth.md`
4. Score using `private/rubrics.md`

### Sending to Candidates

Candidates receive a **separate repo** with only the `candidate/` contents:

- Candidate repo: `https://github.com/oucru-id/spheres_it_task_november_2026_lobar_candidate`
- See `DISTRIBUTION.md` for full instructions

**This repo must stay private.** It contains answer keys, reference implementations, and grading tools.

## Key Files for Quick Reference

| Need | File |
|------|------|
| How to grade step by step | `private/HOW_TO_GRADE.md` |
| Scoring rubrics | `private/rubrics.md` |
| Task 1 defect list | `private/task1-answer-key/defects.md` |
| Task 2 design answer key | `private/task2-reference/design-answer-key.md` |
| Task 3 correct numbers | `private/task3-answer-key/ground-truth.md` |
| How to send to candidates | `DISTRIBUTION.md` |

## Questions?

Contact bwidhiyanto@oucru.org or mputra@oucru.org.
