-- Reference solution: Interpretation 1
-- One visit per patient per day, cancelled excluded, duplicates resolved,
-- facility rename merged, UTC timestamps adjusted to WIB (UTC+7)

WITH normalized_visits AS (
    SELECT
        v.patient_id,
        -- Merge renamed facility
        CASE
            WHEN v.clinic_id = 'PKM-002-OLD' THEN 'PKM-002'
            ELSE v.clinic_id
        END AS clinic_id,
        -- Normalize timestamps: UTC (Z suffix) -> add 7 hours for WIB
        CASE
            WHEN v.visit_date LIKE '%Z'
            THEN date(substr(v.visit_date, 1, 10), '+7 hours')
            ELSE substr(v.visit_date, 1, 10)
        END AS visit_day,
        CASE
            WHEN v.visit_date LIKE '%Z'
            THEN substr(date(substr(v.visit_date, 1, 10), '+7 hours'), 1, 7)
            ELSE substr(v.visit_date, 1, 7)
        END AS month,
        r.registration_number,
        r.status
    FROM visits v
    JOIN registrations r ON v.registration_id = r.id
    WHERE r.status = 'active'
),
-- Deduplicate: same patient, same day, same clinic = 1 visit
-- Also handles retry duplicates (same registration_number)
deduped AS (
    SELECT DISTINCT
        patient_id,
        clinic_id,
        month,
        visit_day
    FROM normalized_visits
)
SELECT
    c.name AS facility_name,
    d.clinic_id,
    d.month,
    COUNT(DISTINCT d.patient_id) AS unique_patients,
    COUNT(*) AS total_visits
FROM deduped d
JOIN clinics c ON c.id = d.clinic_id
GROUP BY d.clinic_id, d.month
ORDER BY d.clinic_id, d.month;
