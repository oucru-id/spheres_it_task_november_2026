# Task 3: Anomaly Catalog

## A1: "Visit" is ambiguous — same patient visits 2+ polyclinics on same day

**Count:** ~1,065 patient-days with multiple polyclinic visits
**Detection SQL:**
```sql
SELECT patient_id, substr(visit_date, 1, 10) as day, COUNT(DISTINCT polyclinic) as polys
FROM visits GROUP BY patient_id, day HAVING polys > 1;
```
**Impact:** Depending on interpretation, "total visits" changes by ~5-8%. A patient seeing both `umum` and `gigi` on the same day could be 1 visit or 2.

## A2: Cancelled registrations still have visit rows

**Count:** ~680 visits linked to cancelled/no-show registrations
**Detection SQL:**
```sql
SELECT COUNT(*) FROM registrations r
JOIN visits v ON v.registration_id = r.id
WHERE r.status IN ('cancelled', 'no_show');
```
**Impact:** ~4% of visits should arguably be excluded. Inflates visit counts.

## A3: Placeholder NIK `0000000000000000` shared by ~303 people

**Count:** 303 patient records with placeholder NIK
**Detection SQL:**
```sql
SELECT COUNT(*) FROM patients WHERE nik = '0000000000000000';
```
**Impact:** `COUNT(DISTINCT nik)` treats all 303 as one person, severely undercounting unique patients.

## A4: Name-variant duplicates

**Count:** ~78 groups of patients with same NIK + birth_date but different name spellings
**Detection SQL:**
```sql
SELECT nik, birth_date, GROUP_CONCAT(DISTINCT name) as names, COUNT(DISTINCT name) as cnt
FROM patients
WHERE nik != '0000000000000000'
GROUP BY nik, birth_date
HAVING cnt > 1;
```
**Impact:** Same person counted multiple times. "Siti Aminah" / "St. Aminah" / "SITI AMINAH" are three patient records for one person.

## A5: Infants registered under mother's NIK

**Count:** ~80 infant records sharing NIK with an adult female patient
**Detection SQL:**
```sql
SELECT child.id, child.name, child.birth_date, child.nik,
       mother.id as mother_id, mother.name as mother_name, mother.birth_date as mother_dob
FROM patients child
JOIN patients mother ON child.nik = mother.nik
    AND child.id != mother.id
    AND mother.gender = 'F'
    AND mother.birth_date < '2000-01-01'
WHERE child.birth_date >= '2024-01-01'
    AND child.nik != '0000000000000000';
```
**Impact:** `COUNT(DISTINCT nik)` merges mother and infant into one person.

## A6: Retry duplicate registrations

**Count:** ~279 duplicate registration_number pairs
**Detection SQL:**
```sql
SELECT registration_number, COUNT(*) as cnt,
       GROUP_CONCAT(id) as reg_ids
FROM registrations
GROUP BY registration_number
HAVING cnt > 1;
```
**Impact:** ~1.5% inflated visit count from system retry duplicates (same registration_number, different row IDs, timestamps seconds apart).

## A7: Mixed timestamps — one clinic stores UTC for 2 months

**Count:** ~1,047 visits with `Z` suffix (UTC), plus ~393 naive UTC (no Z) in PKM-003 for March-April
**Detection SQL:**
```sql
SELECT COUNT(*), visit_date LIKE '%Z' as has_z
FROM visits
WHERE clinic_id = 'PKM-003'
AND substr(visit_date, 1, 7) IN ('2026-03', '2026-04')
GROUP BY has_z;
```
**Impact:** UTC timestamps are 7 hours behind WIB. Visits near midnight land in the wrong month when grouped naively. Early-morning UTC visits (e.g., `01:00Z` = `08:00 WIB`) appear as previous day.

## A8: Implausible records

**Count:** ~16 future birth dates (after 2026-06-30), ~14 birth dates before 1906 (age > 120)
**Detection SQL:**
```sql
SELECT * FROM patients WHERE birth_date > '2026-06-30' OR birth_date < '1906-01-01';
```
**Impact:** Should be flagged for data quality review. May or may not be excluded from patient counts.

## A9: Facility renamed mid-period

**Count:** 1 facility — "Puskesmas Gunungsari" (PKM-002-OLD) became "Puskesmas Gunungsari Timur" (PKM-002) from April onward
**Detection SQL:**
```sql
SELECT id, name FROM clinics WHERE id LIKE 'PKM-002%';
-- Also visible in visit distribution:
SELECT clinic_id, substr(visit_date, 1, 7) as month, COUNT(*)
FROM visits WHERE clinic_id LIKE 'PKM-002%'
GROUP BY clinic_id, month;
```
**Impact:** Naive grouping by `clinic_id` shows two separate facilities instead of one, splitting their 6-month trend.
