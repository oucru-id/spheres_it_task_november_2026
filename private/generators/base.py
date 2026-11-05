"""Shared utilities for data generation: Faker, NIK, clinics."""

import random
import uuid
from datetime import date, datetime, timedelta

from faker import Faker

SEED = 42

fake = Faker("id_ID")
fake.seed_instance(SEED)
rng = random.Random(SEED)


CLINICS = [
    {"id": "PKM-001", "name": "Puskesmas Sandik Raya", "timezone": "Asia/Makassar", "region_code": "5201"},
    {"id": "PKM-002", "name": "Puskesmas Gunungsari Timur", "timezone": "Asia/Makassar", "region_code": "5201"},
    {"id": "PKM-003", "name": "Puskesmas Kalimanah Wetan", "timezone": "Asia/Jakarta", "region_code": "3303"},
]

POLYCLINICS = ["umum", "gigi", "kia", "lansia"]
POLYCLINIC_WEIGHTS = [55, 15, 20, 10]

DIAGNOSES = [
    "ISPA", "Diare", "Hipertensi", "Diabetes mellitus tipe 2", "Demam",
    "Gastritis", "Dermatitis", "Myalgia", "Cephalgia", "Anemia",
    "Faringitis", "Konjungtivitis", "ISK", "Asma bronkiale", "Vertigo",
    "Dispepsia", "Artritis", "Bronkitis", "Rhinitis alergi", "Otitis media",
]

MEDICINES = [
    ("MED-001", "Paracetamol 500mg", "tablet"),
    ("MED-002", "Amoxicillin 500mg", "kaplet"),
    ("MED-003", "ORS (Oralit)", "sachet"),
    ("MED-004", "Ibuprofen 400mg", "tablet"),
    ("MED-005", "Metformin 500mg", "tablet"),
    ("MED-006", "Salbutamol Inhaler", "botol"),
    ("MED-007", "Vitamin B Complex", "tablet"),
    ("MED-008", "Antasida DOEN", "tablet"),
]


def generate_nik(region_code: str, birth_date: date, gender: str, serial: int) -> str:
    day = birth_date.day
    if gender == "F":
        day += 40
    date_part = f"{day:02d}{birth_date.month:02d}{birth_date.year % 100:02d}"
    return f"{region_code}{date_part}{serial:04d}{rng.randint(10, 99)}"


def generate_uuid() -> str:
    return str(uuid.UUID(int=rng.getrandbits(128), version=4))


def random_date_in_range(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=rng.randint(0, delta))


def random_time_on_date(d: date, clinic_tz: str = None) -> datetime:
    if rng.random() < 0.85:
        hour = rng.randint(7, 14)
    else:
        hour = rng.randint(7, 11)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return datetime(d.year, d.month, d.day, hour, minute, second)


def is_weekday(d: date) -> bool:
    return d.weekday() < 5


def should_have_weekend_visit(d: date) -> bool:
    if d.weekday() == 5:
        return rng.random() < 0.15
    return False
