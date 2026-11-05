# Visit Episodes

A Puskesmas (community health clinic) tracks patient visits. For reporting, they want to group a patient's visits into **episodes of care** - a series of related visits.

## Problem

Given a list of visits, each with `patient_id` and `visit_date` (a date string `YYYY-MM-DD`), group each patient's visits into **episodes**.

A **new episode** starts when **more than 14 days** have passed since the patient's previous visit. Otherwise, the visit belongs to the current episode.

Return a list of episodes, each with:
- `patient_id`
- `start_date` (date of the first visit in the episode)
- `end_date` (date of the last visit in the episode)
- `visit_count` (number of visits in the episode)

## Example

```json
[
  {"patient_id": "P1", "visit_date": "2026-01-01"},
  {"patient_id": "P1", "visit_date": "2026-01-10"},
  {"patient_id": "P1", "visit_date": "2026-01-30"},
  {"patient_id": "P1", "visit_date": "2026-02-05"}
]
```

Output:
```json
[
  {"patient_id": "P1", "start_date": "2026-01-01", "end_date": "2026-01-10", "visit_count": 2},
  {"patient_id": "P1", "start_date": "2026-01-30", "end_date": "2026-02-05", "visit_count": 2}
]
```

- Jan 1 to Jan 10: 9 days apart, same episode.
- Jan 10 to Jan 30: 20 days apart (> 14), new episode.
- Jan 30 to Feb 5: 6 days apart, same episode.

## Your Task

Write a function that takes the visit list and returns the list of episodes.
