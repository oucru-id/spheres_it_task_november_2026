# Task 3 Answer Key — Dinkes Report

Contains anomaly catalog, ground truth numbers, reference SQL, and clarifying question rubric.

## Directory Structure

```
task3-answer-key/
├── anomalies.md                  ← A1-A9 with exact counts, example IDs, detection SQL
├── ground-truth.md               ← Correct numbers under 3 interpretations
├── reference-solution.sql        ← CTE-based query for Interpretation 1
├── good-clarifying-questions.md  ← Strong/acceptable/weak question examples
└── generation_stats.json         ← Raw stats from data generator
```

## Anomaly Summary (A1-A9)

| # | Anomaly | Scale | Detection Difficulty |
|---|---------|-------|---------------------|
| A1 | Multi-polyclinic visits (same patient, same day, different polyclinic) | ~6% of patient-days | Medium |
| A2 | Cancelled registrations with visit rows | ~680 rows (~4%) | Easy |
| A3 | Placeholder NIK (0000000000000000) | ~303 patients | Easy |
| A4 | Name variants (same person, different spelling) | ~150 patients | Hard |
| A5 | Infants registered under mother's NIK | ~80 patients | Hard |
| A6 | Retry duplicate registrations (same patient+clinic+time within minutes) | ~1.5% | Medium |
| A7 | Mixed UTC/local timestamps (one clinic, 2 months) | 1 clinic | Medium |
| A8 | Implausible records (birth_date in future, age >120) | ~30 patients | Easy |
| A9 | Facility rename (PKM-002 → PKM-002-OLD mid-period) | 1 facility | Easy-Medium |

Full details with detection SQL in `anomalies.md`.

## Ground Truth (3 Interpretations)

`ground-truth.md` has correct numbers under 3 interpretations:

1. **Interpretation 1** (recommended): One visit per patient per calendar day, anomalies cleaned
2. **Interpretation 2**: One visit per polyclinic attendance, anomalies cleaned
3. **Interpretation 3** (naive): Raw counts, no anomaly handling — the "trap" result

## How to Evaluate

### Step 1: Which interpretation did candidate use?

Compare their result table row-by-row against `ground-truth.md`.

- Match **Interpretation 3** → they didn't find anomalies (weak signal)
- Match **Interpretation 1 or 2** → they found and cleaned anomalies (strong signal)
- Match none → check if internally consistent with their stated assumptions

### Step 2: How many anomalies found?

Read candidate's ASSUMPTIONS.md, compare against `anomalies.md`:

- **7+/9**: Strong — found subtler ones too
- **5-6/9**: Acceptable — found obvious ones, missed A4/A5/A7
- **≤4/9**: Weak — surface-level or naive

### Step 3: Quick naive-trap check

Did candidate fall for these?
- PKM-002-OLD shows as separate facility → missed A9
- `COUNT(DISTINCT nik)` used without caveats → missed A3/A4/A5
- Cancelled registrations included in visit count → missed A2

### Step 4: Clarifying question quality

Compare against `good-clarifying-questions.md`:

- **Strong**: Changes the answer — "Does multi-polyclinic = 1 or 2 visits?"
- **Weak**: Doesn't change answer — "Is the data clean?"
- **Red flag**: Reveals AI-generated anomaly list candidate doesn't understand

## Reference SQL

`reference-solution.sql` — CTE-based query for Interpretation 1. Use to verify candidate's numbers or spot-check specific anomalies.

```bash
sqlite3 candidate/task3-dinkes-report/clinic_data.sqlite < private/task3-answer-key/reference-solution.sql
```
