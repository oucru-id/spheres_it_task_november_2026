"""Generate clinic_data.sqlite for Task 3 with planted anomalies A1-A9.

Deterministic: same seed produces identical output.

Anomalies:
  A1: Same patient visits 2+ polyclinics on same day (~6% of patient-days)
  A2: Cancelled/no-show registrations still have visit rows (~4%)
  A3: Placeholder NIK 0000000000000000 shared by ~200 people
  A4: Name-variant duplicates (~150 people with 2-3 records)
  A5: Infants under mother's NIK (~80)
  A6: Retry duplicate registrations (~1.5%)
  A7: Mixed timestamps - one clinic stores UTC for 2 months
  A8: Implausible birth dates (~30 records)
  A9: Facility renamed mid-period (1 facility)
"""

import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from base import (
    CLINICS, DIAGNOSES, MEDICINES, POLYCLINICS, POLYCLINIC_WEIGHTS,
    fake, generate_nik, generate_uuid, is_weekday, random_date_in_range,
    random_time_on_date, rng, should_have_weekend_visit,
)

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "candidate", "task3-dinkes-report", "clinic_data.sqlite"
)
ANSWER_KEY_PATH = os.path.join(os.path.dirname(__file__), "..", "task3-answer-key")

START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 6, 30)

TARGET_VISITS = 20000
CLINIC_WEIGHTS = {"PKM-001": 0.50, "PKM-002": 0.25, "PKM-003": 0.25}

NAME_VARIANTS = {
    "Siti": ["St.", "SITI", "Siti"],
    "Muhammad": ["Muh.", "MUH", "Muhammad"],
    "Ahmad": ["Ah.", "AHMAD", "Ahmad"],
    "Abdul": ["Abd.", "ABDUL", "Abdul"],
    "Dewi": ["Dw.", "DEWI", "Dewi"],
    "Sri": ["Sr.", "SRI", "Sri"],
    "Nur": ["Nr.", "NUR", "Nur"],
}


def create_schema(conn):
    conn.executescript("""
        CREATE TABLE clinics (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            timezone TEXT NOT NULL,
            region_code TEXT NOT NULL
        );

        CREATE TABLE patients (
            id TEXT PRIMARY KEY,
            nik TEXT NOT NULL,
            name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            gender TEXT NOT NULL,
            address TEXT,
            clinic_id TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE registrations (
            id TEXT PRIMARY KEY,
            registration_number TEXT NOT NULL,
            patient_id TEXT,
            clinic_id TEXT,
            registered_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            polyclinic TEXT NOT NULL
        );

        CREATE TABLE visits (
            id TEXT PRIMARY KEY,
            registration_id TEXT,
            patient_id TEXT,
            clinic_id TEXT,
            polyclinic TEXT NOT NULL,
            visit_date TEXT NOT NULL,
            diagnosis TEXT,
            notes TEXT
        );

        CREATE TABLE dispensing (
            id TEXT PRIMARY KEY,
            visit_id TEXT,
            patient_id TEXT,
            medicine_id TEXT,
            quantity INTEGER NOT NULL,
            dispensed_at TEXT NOT NULL
        );
    """)


def insert_clinics(conn):
    # A9: Facility renamed mid-period
    # PKM-002 was "Puskesmas Gunungsari" for Jan-Mar, renamed to "Puskesmas Gunungsari Timur" from Apr
    clinics_data = []
    for c in CLINICS:
        if c["id"] == "PKM-002":
            clinics_data.append(("PKM-002", "Puskesmas Gunungsari Timur", c["timezone"], c["region_code"]))
            clinics_data.append(("PKM-002-OLD", "Puskesmas Gunungsari", c["timezone"], c["region_code"]))
        else:
            clinics_data.append((c["id"], c["name"], c["timezone"], c["region_code"]))

    conn.executemany(
        "INSERT INTO clinics (id, name, timezone, region_code) VALUES (?, ?, ?, ?)",
        clinics_data,
    )


def generate_patients(conn):
    patients = []
    patient_index = {}
    nik_serial = defaultdict(int)

    normal_count = 2800
    for i in range(normal_count):
        clinic = rng.choices(list(CLINIC_WEIGHTS.keys()), weights=list(CLINIC_WEIGHTS.values()))[0]
        clinic_data = next(c for c in CLINICS if c["id"] == clinic)
        region = clinic_data["region_code"]

        gender = rng.choice(["M", "F"])
        if gender == "M":
            name = fake.first_name_male() + " " + fake.last_name()
        else:
            name = fake.first_name_female() + " " + fake.last_name()

        birth_date = random_date_in_range(date(1950, 1, 1), date(2020, 12, 31))

        nik_serial[region] += 1
        nik = generate_nik(region, birth_date, gender, nik_serial[region])

        pid = generate_uuid()
        created = random_date_in_range(date(2025, 6, 1), date(2025, 12, 31))

        patients.append({
            "id": pid, "nik": nik, "name": name, "birth_date": birth_date.isoformat(),
            "gender": gender, "address": fake.address(), "clinic_id": clinic,
            "created_at": datetime(created.year, created.month, created.day, 8, 0, 0).isoformat(),
        })
        patient_index[pid] = patients[-1]

    # A3: ~200 patients with placeholder NIK
    a3_ids = []
    for i in range(200):
        clinic = rng.choices(list(CLINIC_WEIGHTS.keys()), weights=list(CLINIC_WEIGHTS.values()))[0]
        gender = rng.choice(["M", "F"])
        if gender == "M":
            name = fake.first_name_male() + " " + fake.last_name()
        else:
            name = fake.first_name_female() + " " + fake.last_name()
        birth_date = random_date_in_range(date(1960, 1, 1), date(2015, 12, 31))
        pid = generate_uuid()
        created = random_date_in_range(date(2025, 6, 1), date(2025, 12, 31))

        patients.append({
            "id": pid, "nik": "0000000000000000", "name": name,
            "birth_date": birth_date.isoformat(), "gender": gender,
            "address": fake.address(), "clinic_id": clinic,
            "created_at": datetime(created.year, created.month, created.day, 8, 0, 0).isoformat(),
        })
        patient_index[pid] = patients[-1]
        a3_ids.append(pid)

    # A4: ~150 name-variant duplicate patients
    a4_groups = []
    for i in range(150):
        clinic = rng.choices(list(CLINIC_WEIGHTS.keys()), weights=list(CLINIC_WEIGHTS.values()))[0]
        clinic_data = next(c for c in CLINICS if c["id"] == clinic)
        region = clinic_data["region_code"]
        gender = rng.choice(["M", "F"])

        if gender == "F":
            first_names = rng.choice(list(NAME_VARIANTS.keys()))
            variants = NAME_VARIANTS[first_names]
        else:
            first_names = rng.choice(["Muhammad", "Ahmad", "Abdul"])
            variants = NAME_VARIANTS[first_names]

        last_name = fake.last_name()
        birth_date = random_date_in_range(date(1960, 1, 1), date(2010, 12, 31))

        nik_serial[region] += 1
        real_nik = generate_nik(region, birth_date, gender, nik_serial[region])

        group_ids = []
        num_variants = rng.choice([2, 2, 2, 3])
        chosen_variants = rng.sample(variants, min(num_variants, len(variants)))

        for vi, variant in enumerate(chosen_variants):
            pid = generate_uuid()
            full_name = f"{variant} {last_name}"
            created = random_date_in_range(date(2025, 6, 1), date(2025, 12, 31))

            p = {
                "id": pid, "name": full_name,
                "birth_date": birth_date.isoformat(), "gender": gender,
                "address": fake.address(), "clinic_id": clinic,
                "created_at": datetime(created.year, created.month, created.day, 8, 0, 0).isoformat(),
            }
            if vi == 0:
                p["nik"] = real_nik
            elif rng.random() < 0.5:
                p["nik"] = real_nik
            else:
                p["nik"] = "0000000000000000"

            patients.append(p)
            patient_index[pid] = patients[-1]
            group_ids.append(pid)

        a4_groups.append({"nik": real_nik, "birth_date": birth_date.isoformat(), "ids": group_ids})

    # A5: ~80 infants under mother's NIK
    a5_pairs = []
    mothers = [p for p in patients if p["gender"] == "F" and p["nik"] != "0000000000000000"
               and int(p["birth_date"][:4]) < 2000]
    selected_mothers = rng.sample(mothers, min(80, len(mothers)))

    for mother in selected_mothers:
        infant_birth = random_date_in_range(date(2024, 6, 1), date(2026, 3, 31))
        infant_gender = rng.choice(["M", "F"])
        if infant_gender == "M":
            infant_name = fake.first_name_male() + " " + mother["name"].split()[-1]
        else:
            infant_name = fake.first_name_female() + " " + mother["name"].split()[-1]

        pid = generate_uuid()
        created = random_date_in_range(date(2025, 9, 1), date(2026, 1, 31))

        patients.append({
            "id": pid, "nik": mother["nik"], "name": infant_name,
            "birth_date": infant_birth.isoformat(), "gender": infant_gender,
            "address": mother["address"], "clinic_id": mother["clinic_id"],
            "created_at": datetime(created.year, created.month, created.day, 8, 0, 0).isoformat(),
        })
        patient_index[pid] = patients[-1]
        a5_pairs.append({"mother_id": mother["id"], "infant_id": pid, "shared_nik": mother["nik"]})

    # A8: ~30 implausible records
    a8_ids = []
    for i in range(30):
        clinic = rng.choices(list(CLINIC_WEIGHTS.keys()), weights=list(CLINIC_WEIGHTS.values()))[0]
        gender = rng.choice(["M", "F"])
        if gender == "M":
            name = fake.first_name_male() + " " + fake.last_name()
        else:
            name = fake.first_name_female() + " " + fake.last_name()

        if rng.random() < 0.5:
            birth_date = random_date_in_range(date(2027, 1, 1), date(2028, 12, 31))
        else:
            birth_date = random_date_in_range(date(1890, 1, 1), date(1905, 12, 31))

        clinic_data = next(c for c in CLINICS if c["id"] == clinic)
        nik_serial[clinic_data["region_code"]] += 1
        nik = generate_nik(clinic_data["region_code"], date(1990, 1, 1), gender,
                           nik_serial[clinic_data["region_code"]])

        pid = generate_uuid()
        patients.append({
            "id": pid, "nik": nik, "name": name,
            "birth_date": birth_date.isoformat(), "gender": gender,
            "address": fake.address(), "clinic_id": clinic,
            "created_at": "2025-10-01T08:00:00",
        })
        patient_index[pid] = patients[-1]
        a8_ids.append(pid)

    conn.executemany(
        "INSERT INTO patients (id, nik, name, birth_date, gender, address, clinic_id, created_at) "
        "VALUES (:id, :nik, :name, :birth_date, :gender, :address, :clinic_id, :created_at)",
        patients,
    )

    return patients, patient_index, {
        "a3_ids": a3_ids,
        "a4_groups": a4_groups,
        "a5_pairs": a5_pairs,
        "a8_ids": a8_ids,
    }


def generate_visits(conn, patients, patient_index, anomaly_info):
    registrations = []
    visits = []
    dispensing_records = []

    patient_ids_by_clinic = defaultdict(list)
    for p in patients:
        patient_ids_by_clinic[p["clinic_id"]].append(p["id"])

    reg_counter = defaultdict(int)
    a1_count = 0
    a2_count = 0
    a6_count = 0
    a7_affected = []

    current_date = START_DATE
    visit_count = 0

    while current_date <= END_DATE and visit_count < TARGET_VISITS:
        for clinic_id, weight in CLINIC_WEIGHTS.items():
            if not is_weekday(current_date) and not should_have_weekend_visit(current_date):
                continue

            # A9: PKM-002 uses old name for Jan-Mar
            effective_clinic_id = clinic_id
            if clinic_id == "PKM-002" and current_date.month <= 3:
                effective_clinic_id = "PKM-002-OLD"

            daily_target = int(rng.gauss(weight * 130, weight * 15))
            daily_target = max(5, daily_target)

            clinic_patients = patient_ids_by_clinic.get(clinic_id, [])
            if not clinic_patients:
                continue

            daily_patients = rng.sample(clinic_patients, min(daily_target, len(clinic_patients)))

            for pid in daily_patients:
                if visit_count >= TARGET_VISITS:
                    break

                patient = patient_index[pid]
                poly = rng.choices(POLYCLINICS, weights=POLYCLINIC_WEIGHTS)[0]

                reg_counter[clinic_id] += 1
                reg_num = f"{clinic_id}-{reg_counter[clinic_id]:06d}"
                reg_id = generate_uuid()
                visit_id = generate_uuid()

                visit_time = random_time_on_date(current_date)

                # A2: ~4% cancelled/no-show registrations
                status = "active"
                if rng.random() < 0.04:
                    status = rng.choice(["cancelled", "no_show"])
                    a2_count += 1

                # A7: PKM-003 stores UTC timestamps for Mar-Apr
                visit_date_str = visit_time.isoformat()
                if clinic_id == "PKM-003" and current_date.month in (3, 4):
                    utc_time = visit_time - timedelta(hours=7)
                    if rng.random() < 0.7:
                        visit_date_str = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    else:
                        visit_date_str = utc_time.strftime("%Y-%m-%dT%H:%M:%S")
                    a7_affected.append(visit_id)

                registrations.append({
                    "id": reg_id, "registration_number": reg_num,
                    "patient_id": pid, "clinic_id": effective_clinic_id,
                    "registered_at": visit_time.isoformat(),
                    "status": status, "polyclinic": poly,
                })

                visits.append({
                    "id": visit_id, "registration_id": reg_id,
                    "patient_id": pid, "clinic_id": effective_clinic_id,
                    "polyclinic": poly, "visit_date": visit_date_str,
                    "diagnosis": rng.choice(DIAGNOSES),
                    "notes": fake.sentence() if rng.random() < 0.3 else None,
                })
                visit_count += 1

                # A1: ~6% multi-polyclinic same day
                if rng.random() < 0.06:
                    other_polys = [p for p in POLYCLINICS if p != poly]
                    poly2 = rng.choice(other_polys)
                    reg_counter[clinic_id] += 1
                    reg_num2 = f"{clinic_id}-{reg_counter[clinic_id]:06d}"
                    reg_id2 = generate_uuid()
                    visit_id2 = generate_uuid()
                    visit_time2 = visit_time + timedelta(hours=rng.randint(1, 3))

                    visit_date_str2 = visit_time2.isoformat()
                    if clinic_id == "PKM-003" and current_date.month in (3, 4):
                        utc_time2 = visit_time2 - timedelta(hours=7)
                        if rng.random() < 0.7:
                            visit_date_str2 = utc_time2.strftime("%Y-%m-%dT%H:%M:%SZ")
                        else:
                            visit_date_str2 = utc_time2.strftime("%Y-%m-%dT%H:%M:%S")

                    registrations.append({
                        "id": reg_id2, "registration_number": reg_num2,
                        "patient_id": pid, "clinic_id": effective_clinic_id,
                        "registered_at": visit_time2.isoformat(),
                        "status": "active", "polyclinic": poly2,
                    })
                    visits.append({
                        "id": visit_id2, "registration_id": reg_id2,
                        "patient_id": pid, "clinic_id": effective_clinic_id,
                        "polyclinic": poly2, "visit_date": visit_date_str2,
                        "diagnosis": rng.choice(DIAGNOSES),
                        "notes": None,
                    })
                    visit_count += 1
                    a1_count += 1

                # A6: ~1.5% retry duplicates
                if rng.random() < 0.015:
                    dup_reg_id = generate_uuid()
                    dup_visit_id = generate_uuid()
                    dup_time = visit_time + timedelta(seconds=rng.randint(1, 5))

                    registrations.append({
                        "id": dup_reg_id, "registration_number": reg_num,
                        "patient_id": pid, "clinic_id": effective_clinic_id,
                        "registered_at": dup_time.isoformat(),
                        "status": status, "polyclinic": poly,
                    })
                    visits.append({
                        "id": dup_visit_id, "registration_id": dup_reg_id,
                        "patient_id": pid, "clinic_id": effective_clinic_id,
                        "polyclinic": poly, "visit_date": dup_time.isoformat(),
                        "diagnosis": visits[-1]["diagnosis"] if not (clinic_id == "PKM-003" and current_date.month in (3, 4)) else visits[-1]["diagnosis"],
                        "notes": visits[-1]["notes"],
                    })
                    visit_count += 1
                    a6_count += 1

                # Dispensing for some visits
                if rng.random() < 0.6 and status == "active":
                    med = rng.choice(MEDICINES)
                    qty = rng.randint(5, 30)
                    dispensing_records.append({
                        "id": generate_uuid(), "visit_id": visit_id,
                        "patient_id": pid, "medicine_id": med[0],
                        "quantity": qty,
                        "dispensed_at": visit_time.isoformat(),
                    })

        current_date += timedelta(days=1)

    conn.executemany(
        "INSERT INTO registrations (id, registration_number, patient_id, clinic_id, registered_at, status, polyclinic) "
        "VALUES (:id, :registration_number, :patient_id, :clinic_id, :registered_at, :status, :polyclinic)",
        registrations,
    )
    conn.executemany(
        "INSERT INTO visits (id, registration_id, patient_id, clinic_id, polyclinic, visit_date, diagnosis, notes) "
        "VALUES (:id, :registration_id, :patient_id, :clinic_id, :polyclinic, :visit_date, :diagnosis, :notes)",
        visits,
    )
    conn.executemany(
        "INSERT INTO dispensing (id, visit_id, patient_id, medicine_id, quantity, dispensed_at) "
        "VALUES (:id, :visit_id, :patient_id, :medicine_id, :quantity, :dispensed_at)",
        dispensing_records,
    )

    return {
        "total_visits": len(visits),
        "total_registrations": len(registrations),
        "total_dispensing": len(dispensing_records),
        "a1_multi_poly_count": a1_count,
        "a2_cancelled_count": a2_count,
        "a6_retry_dup_count": a6_count,
        "a7_affected_visits": len(a7_affected),
    }


def compute_answer_key(conn):
    stats = {}

    # Naive result
    naive = conn.execute("""
        SELECT
            v.clinic_id,
            substr(v.visit_date, 1, 7) as month,
            COUNT(*) as total_visits,
            COUNT(DISTINCT p.nik) as unique_patients_by_nik
        FROM visits v
        JOIN patients p ON v.patient_id = p.id
        GROUP BY v.clinic_id, substr(v.visit_date, 1, 7)
        ORDER BY v.clinic_id, month
    """).fetchall()
    stats["naive"] = [dict(r) for r in naive]

    # Anomaly counts
    a2 = conn.execute("SELECT COUNT(*) FROM registrations WHERE status IN ('cancelled', 'no_show')").fetchone()[0]
    a3 = conn.execute("SELECT COUNT(*) FROM patients WHERE nik = '0000000000000000'").fetchone()[0]
    a6 = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT registration_number, COUNT(*) as cnt
            FROM registrations
            GROUP BY registration_number
            HAVING cnt > 1
        )
    """).fetchone()[0]
    a8_future = conn.execute("SELECT COUNT(*) FROM patients WHERE birth_date > '2026-06-30'").fetchone()[0]
    a8_old = conn.execute("SELECT COUNT(*) FROM patients WHERE birth_date < '1906-01-01'").fetchone()[0]
    a9 = conn.execute("SELECT COUNT(DISTINCT name) FROM clinics WHERE id LIKE 'PKM-002%'").fetchone()[0]

    stats["anomaly_counts"] = {
        "a2_cancelled_registrations": a2,
        "a3_placeholder_nik_patients": a3,
        "a6_duplicate_reg_numbers": a6,
        "a8_implausible_future": a8_future,
        "a8_implausible_old": a8_old,
        "a9_facility_name_variants": a9,
    }

    return stats


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)

    conn = sqlite3.connect(OUTPUT_PATH)
    conn.row_factory = sqlite3.Row

    print("Creating schema...")
    create_schema(conn)

    print("Inserting clinics...")
    insert_clinics(conn)

    print("Generating patients...")
    patients, patient_index, anomaly_info = generate_patients(conn)
    print(f"  Created {len(patients)} patients")
    print(f"  A3 placeholder NIK: {len(anomaly_info['a3_ids'])}")
    print(f"  A4 name-variant groups: {len(anomaly_info['a4_groups'])}")
    print(f"  A5 infant-mother pairs: {len(anomaly_info['a5_pairs'])}")
    print(f"  A8 implausible: {len(anomaly_info['a8_ids'])}")

    print("Generating visits...")
    visit_stats = generate_visits(conn, patients, patient_index, anomaly_info)
    print(f"  Total visits: {visit_stats['total_visits']}")
    print(f"  A1 multi-polyclinic: {visit_stats['a1_multi_poly_count']}")
    print(f"  A2 cancelled: {visit_stats['a2_cancelled_count']}")
    print(f"  A6 retry dups: {visit_stats['a6_retry_dup_count']}")
    print(f"  A7 UTC timestamps: {visit_stats['a7_affected_visits']}")

    conn.commit()

    print("Computing answer key stats...")
    stats = compute_answer_key(conn)

    os.makedirs(ANSWER_KEY_PATH, exist_ok=True)
    with open(os.path.join(ANSWER_KEY_PATH, "generation_stats.json"), "w") as f:
        json.dump({
            "patients": len(patients),
            "anomaly_info": {
                "a3_count": len(anomaly_info["a3_ids"]),
                "a4_groups": len(anomaly_info["a4_groups"]),
                "a5_pairs": len(anomaly_info["a5_pairs"]),
                "a8_count": len(anomaly_info["a8_ids"]),
            },
            "visit_stats": visit_stats,
            "naive_results": stats["naive"],
            "anomaly_counts": stats["anomaly_counts"],
        }, f, indent=2, default=str)

    conn.close()
    print(f"\nGenerated: {OUTPUT_PATH}")
    print(f"Stats saved: {ANSWER_KEY_PATH}/generation_stats.json")


if __name__ == "__main__":
    main()
