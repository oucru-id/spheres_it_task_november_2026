# Task 3: Ground Truth Numbers

## Interpretation 1: One visit per patient per day (recommended)

Cancelled/no-show excluded, retry duplicates resolved, facility rename merged, UTC timestamps adjusted to WIB.

| Facility | Month | Unique Patients | Total Visits |
|----------|-------|-----------------|--------------|
| PKM-001 | 2026-01 | 954 | 1,371 |
| PKM-001 | 2026-02 | 948 | 1,374 |
| PKM-001 | 2026-03 | 922 | 1,300 |
| PKM-001 | 2026-04 | 954 | 1,347 |
| PKM-001 | 2026-05 | 997 | 1,441 |
| PKM-001 | 2026-06 | 1,015 | 1,529 |
| PKM-002 | 2026-01 | 489 | 697 |
| PKM-002 | 2026-02 | 480 | 738 |
| PKM-002 | 2026-03 | 486 | 730 |
| PKM-002 | 2026-04 | 493 | 718 |
| PKM-002 | 2026-05 | 451 | 621 |
| PKM-002 | 2026-06 | 493 | 720 |
| PKM-003 | 2026-01 | 518 | 764 |
| PKM-003 | 2026-02 | 429 | 609 |
| PKM-003 | 2026-03 | 495 | 694 |
| PKM-003 | 2026-04 | 475 | 688 |
| PKM-003 | 2026-05 | 492 | 731 |
| PKM-003 | 2026-06 | 474 | 666 |

## Interpretation 2: One visit per polyclinic attendance

Same cleaning as Interpretation 1, but multi-polyclinic = multiple visits.

| Facility | Month | Unique Patients | Total Visits |
|----------|-------|-----------------|--------------|
| PKM-001 | 2026-01 | 954 | 1,445 |
| PKM-001 | 2026-02 | 948 | 1,451 |
| PKM-001 | 2026-03 | 922 | 1,387 |
| PKM-001 | 2026-04 | 954 | 1,443 |
| PKM-001 | 2026-05 | 997 | 1,523 |
| PKM-001 | 2026-06 | 1,015 | 1,626 |
| PKM-002 | 2026-01 | 489 | 738 |
| PKM-002 | 2026-02 | 480 | 790 |
| PKM-002 | 2026-03 | 486 | 777 |
| PKM-002 | 2026-04 | 493 | 756 |
| PKM-002 | 2026-05 | 451 | 659 |
| PKM-002 | 2026-06 | 493 | 760 |
| PKM-003 | 2026-01 | 518 | 814 |
| PKM-003 | 2026-02 | 429 | 646 |
| PKM-003 | 2026-03 | 495 | 732 |
| PKM-003 | 2026-04 | 475 | 730 |
| PKM-003 | 2026-05 | 492 | 781 |
| PKM-003 | 2026-06 | 474 | 713 |

## Interpretation 3: Naive (what AI tools typically produce)

`COUNT(*)` and `COUNT(DISTINCT nik)` grouped by raw `clinic_id` and raw month.

| Facility | Month | Visits (COUNT *) | Patients (DISTINCT nik) |
|----------|-------|------------------|------------------------|
| PKM-001 | 2026-01 | 1,518 | 857 |
| PKM-001 | 2026-02 | 1,528 | 869 |
| PKM-001 | 2026-03 | 1,471 | 829 |
| PKM-001 | 2026-04 | 1,513 | 861 |
| PKM-001 | 2026-05 | 1,611 | 897 |
| PKM-001 | 2026-06 | 1,722 | 908 |
| PKM-002 | 2026-04 | 796 | 448 |
| PKM-002 | 2026-05 | 695 | 400 |
| PKM-002 | 2026-06 | 807 | 438 |
| PKM-002-OLD | 2026-01 | 782 | 450 |
| PKM-002-OLD | 2026-02 | 827 | 430 |
| PKM-002-OLD | 2026-03 | 811 | 430 |
| PKM-003 | 2026-01 | 861 | 485 |
| PKM-003 | 2026-02 | 677 | 398 |
| PKM-003 | 2026-03 | 782 | 459 |
| PKM-003 | 2026-04 | 760 | 433 |
| PKM-003 | 2026-05 | 816 | 448 |
| PKM-003 | 2026-06 | 747 | 431 |

## Key Differences (Naive vs Clean)

- **Patient counts:** Naive undercounts by ~100-150 per facility-month because `COUNT(DISTINCT nik)` collapses 303 placeholder-NIK patients into 1, merges 80 infants with mothers, and merges ~78 name-variant groups
- **Visit counts:** Naive overcounts by ~100-200 per facility-month because it includes cancelled registrations (~4%), retry duplicates (~1.5%), and doesn't deduplicate multi-polyclinic same-day visits
- **Facility split:** Naive shows "PKM-002-OLD" as a separate facility (Jan-Mar) with no data for Apr-Jun, and "PKM-002" starting from Apr only
- **Month boundary:** Naive places some PKM-003 visits in wrong months (UTC timestamps without adjustment)
