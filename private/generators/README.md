# Generators

Deterministic data generators for assessment materials. All use **seed=42** — same seed = identical output every run.

## Files

| File | Purpose |
|------|---------|
| `base.py` | Shared utilities: Faker (id_ID locale), NIK generator, clinic definitions (3 Puskesmas), seeded RNG |
| `task3_data_generator.py` | Generates `clinic_data.sqlite` with 9 planted anomalies (A1-A9). Output: ~18,700 visits, ~3,450 patients, 4 clinics (including PKM-002-OLD for A9), 6 months of data |
| `requirements.txt` | Python dependencies (Faker) |

## How to Run

```bash
cd private/generators/
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Generate Task 3 SQLite
.venv/bin/python task3_data_generator.py
```

Output goes to `candidate/task3-dinkes-report/clinic_data.sqlite`.

Stats saved to `private/task3-answer-key/generation_stats.json`.

## When to Regenerate

- Changed anomaly parameters (counts, ratios)
- Changed clinic definitions
- Changed schema

After regenerating, update `private/task3-answer-key/ground-truth.md` and `anomalies.md` with new counts.

## Key Design Decisions

- **id_ID locale**: Indonesian names, addresses, phone numbers
- **NIK format**: 16-digit, province+regency+district+DOB+sequence
- **3 clinics**: Sandik Raya (WITA), Gunungsari Timur (WITA), Kalimanah Wetan (WIB) — cross-timezone is intentional for A7
- **PKM-002-OLD**: facility rename artifact for A9
