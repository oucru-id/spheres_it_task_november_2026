# Distribution Guide

How to share this assessment with interviewer teams and candidates.

---

## What Goes Where

| Audience | What They Get | What They Must NOT See |
|----------|--------------|----------------------|
| **Interviewer team** | Full repo (`candidate/` + `private/`) | Nothing hidden — they need everything |
| **Candidate** | Only `candidate/` directory | `private/`, `pompt.md`, `.claude/`, this file |

---

## For Interviewer Teams

### Option A: Full Repo Access (Recommended)

Add interviewers as collaborators on the **private** GitHub repo:

```
https://github.com/oucru-id/spheres_it_task_november_2026
```

They clone the full repo and follow `private/README.md` to get started.

### Option B: Share as ZIP

```bash
# From repo root
git archive --format=zip HEAD -o spheres-assessment-full.zip
```

Send the zip with a note:

> **Subject:** SPHERES IT Assessment — Evaluator Materials
>
> Attached: full assessment repo including answer keys, rubrics, and grading tools.
>
> Start here:
> - `private/README.md` — how to set up and operate the grading tools
> - `private/HOW_TO_GRADE.md` — step-by-step grading workflow
> - `private/rubrics.md` — scoring criteria
> - `private/interview-guide.md` — follow-up call script
>
> **Do not share the `private/` directory or this zip with candidates.**

### What Interviewers Need to Do First

1. Read `private/README.md` (evaluator overview)
2. Set up Python venvs for detection tests and grading harness (one-time, ~5 min)
3. Read `private/rubrics.md` to understand scoring
4. Read `private/interview-guide.md` before the follow-up call

---

## For Candidates

### Step 1: Prepare Candidate Package

Extract only `candidate/` into a separate repo or zip:

```bash
# Option A: Create a zip from candidate/ only
cd /path/to/spheres_it_task_november_2026
zip -r spheres-candidate-package.zip candidate/
```

```bash
# Option B: Create a separate clean repo for candidates
mkdir /tmp/candidate-repo && cd /tmp/candidate-repo
git init
cp -r /path/to/spheres_it_task_november_2026/candidate/* .
git add -A
git commit -m "SPHERES take-home assessment"
```

### Step 2: Fill Placeholders

Before sending, update `candidate/README.md` — search for and replace:

| Placeholder | Replace With |
|-------------|-------------|
| `[GRADER_GITHUB_HANDLE]` | Your GitHub username (for candidate to add as collaborator) |
| `[EMAIL_ADDRESS]` | Contact email for clarifying questions |
| `[SUBJECT_LINE]` | Email subject line format for submissions |

### Step 3: Verify Package

Before sending to any candidate, verify:

- [ ] `private/` directory is NOT in the candidate package
- [ ] `pompt.md` is NOT in the candidate package
- [ ] `.claude/` directory is NOT in the candidate package
- [ ] `DISTRIBUTION.md` (this file) is NOT in the candidate package
- [ ] `.gitignore` doesn't reference private paths
- [ ] No hint words in candidate files: `grep -ri "defect\|anomaly\|planted\|answer.key\|rubric" candidate/`
- [ ] `candidate/task3-dinkes-report/clinic_data.sqlite` is present (binary file, ~2MB)
- [ ] Placeholders in `candidate/README.md` are filled

### Step 4: Send to Candidate

**Email template:**

> **Subject:** [SUBJECT_LINE]
>
> Hi [Name],
>
> Attached is the SPHERES take-home assessment. Please read `README.md` first — it covers task selection, time guidelines, AI policy, and submission format.
>
> Key points:
> - Complete **Task 1** (required) + your choice of **Task 2 or Task 3**
> - Recommended time: 10-11 hours total over 3 calendar days
> - AI tools are allowed — document your usage in `AI_USAGE.md`
> - Submit as a private GitHub repo, add `[GRADER_GITHUB_HANDLE]` as collaborator
>
> For clarifying questions: email [EMAIL_ADDRESS] (one question per task, must be a question that changes your approach)
>
> Good luck!

**Or as a private GitHub repo:**

1. Create repo under `oucru-id` org (private)
2. Push only `candidate/` contents
3. Add candidate as collaborator
4. Send repo link

---

## After Candidate Submits

1. Clone their submission repo
2. Follow `private/HOW_TO_GRADE.md` step by step
3. Use `private/rubrics.md` for scoring
4. Schedule 45-min follow-up call, use `private/interview-guide.md`
5. Calculate final score: `Task 1 (35%) + Chosen Task (35%) + Call (30%)`

---

## Security Checklist

- [ ] GitHub repo `oucru-id/spheres_it_task_november_2026` is **private**
- [ ] Only interviewer team members have access
- [ ] Candidate packages never include `private/`
- [ ] Different candidates get identical packages (no per-candidate customization that could leak)
- [ ] After assessment round, consider rotating the planted defects if reusing
