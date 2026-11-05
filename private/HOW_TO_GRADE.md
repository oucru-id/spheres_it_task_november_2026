# How to Grade

Step-by-step grading process for each candidate submission.

## Before You Start

1. Read their `CHOICE.md` to know which optional task they picked
2. Read their `AI_USAGE.md`

## Task 1: Clinic Sync Service

### Step 1: Run Detection Tests

```bash
cd private/task1-answer-key/detection-tests/

# Point tests at candidate's code
# Edit conftest.py sys.path to point to the candidate's task1 folder

pytest -v --tb=short
```

Each test that **fails** on their code = a defect they didn't fix.
Each test that **passes** = a defect they fixed.

Record which defects they fixed and compare against their REVIEW.md.

### Step 2: Read REVIEW.md

- How many defects did they find? (out of 10)
- Are the top 5 ranked by actual impact?
- Does the impact analysis name stakeholders and concrete consequences?
- Compare their ranking against `private/task1-answer-key/defects.md`

### Step 3: Check Their Fixes

- Did they fix the 3 most impactful issues, or the 3 easiest?
- Does each fix have a test that exercises the actual failure mode?
- Do the existing 11 happy-path tests still pass?

### Step 4: Score

Use `private/rubrics.md` Task 1 rubric.

## Task 2: Offline-First Sync (if chosen)

### Step 1: Start Their Endpoint

Follow their README instructions to start the server on port 8000.

### Step 2: Run Grading Harness

```bash
cd private/task2-reference/
make grade URL=http://localhost:8000
```

If their server is inside Docker:
```bash
make grade URL=http://host.docker.internal:8000
```

Record: X/14 tests pass.

### Step 3: Read DESIGN.md

Compare against `private/task2-reference/design-answer-key.md` for each of the 7 design questions.

### Step 4: Score

Use `private/rubrics.md` Task 2 rubric. Harness score feeds into "Endpoint + Tests" criterion.

## Task 3: Dinkes Report (if chosen)

### Step 1: Compare Numbers

Compare their result table against `private/task3-answer-key/ground-truth.md`.

Determine which interpretation they used:
- Interpretation 1 (one visit per patient per day)
- Interpretation 2 (one visit per polyclinic attendance)
- Something else (check if internally consistent)

If their numbers match the **naive** result exactly (Interpretation 3), they didn't find the anomalies.

### Step 2: Read ASSUMPTIONS.md

Compare against `private/task3-answer-key/anomalies.md`:
- How many of the 9 anomalies did they find?
- Did they handle each one with a stated decision?
- Did they group related issues (A3+A4+A5)?

### Step 3: Check Clarifying Question

Compare against `private/task3-answer-key/good-clarifying-questions.md`:
- Does the question change the answer?
- Is it specific and actionable?

### Step 4: Score

Use `private/rubrics.md` Task 3 rubric.

## Follow-Up Call (60-75 minutes total)

### Part 1: Take-Home Walkthrough (35-40 minutes)

Use `private/interview-guide.md` for the walkthrough script.
Score using the take-home walkthrough rubric in `private/rubrics.md`.

### Part 2: Live Coding Session (30 minutes)

Use `private/interview/live-coding/README.md` for the session guide.
Pick one problem from `private/interview/live-coding/problems/`.
Fill in `private/interview/live-coding/scoring-sheet.md` immediately after.

## Final Score

```
Final = (Task 1 score x 0.35) + (Chosen task score x 0.35) + (Walkthrough x 0.15) + (Live coding x 0.15)
```

Both optional tasks are scored out of 100, so candidates who chose differently are directly comparable.
