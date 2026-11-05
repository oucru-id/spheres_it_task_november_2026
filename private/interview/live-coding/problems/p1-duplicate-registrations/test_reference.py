from reference import find_duplicates


def test_basic_example():
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:03:00+08:00"},
        {"registration_id": "R3", "patient_id": "P100", "puskesmas_id": "PKM-002", "registered_at": "2026-03-15T10:01:00+08:00"},
        {"registration_id": "R4", "patient_id": None,   "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:01:00+08:00"},
    ]
    assert find_duplicates(regs) == ["R2"]


def test_empty_input():
    assert find_duplicates([]) == []


def test_single_registration():
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
    ]
    assert find_duplicates(regs) == []


def test_null_patient_id_never_duplicate():
    regs = [
        {"registration_id": "R1", "patient_id": None, "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
        {"registration_id": "R2", "patient_id": None, "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:01:00+08:00"},
    ]
    assert find_duplicates(regs) == []


def test_unsorted_input():
    regs = [
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:03:00+08:00"},
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
    ]
    assert find_duplicates(regs) == ["R2"]


def test_exactly_5_minutes_is_duplicate():
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:05:00+08:00"},
    ]
    assert find_duplicates(regs) == ["R2"]


def test_5_minutes_1_second_not_duplicate():
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:05:01+08:00"},
    ]
    assert find_duplicates(regs) == []


def test_different_puskesmas_not_duplicate():
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-002", "registered_at": "2026-03-15T10:01:00+08:00"},
    ]
    assert find_duplicates(regs) == []


def test_chaining_compare_against_last_kept():
    """10:00 (kept), 10:04 (dup of 10:00), 10:08 (8 min from 10:00 = not dup)."""
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:04:00+08:00"},
        {"registration_id": "R3", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:08:00+08:00"},
    ]
    assert find_duplicates(regs) == ["R2"]


def test_crossing_midnight():
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T23:58:00+08:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-16T00:01:00+08:00"},
    ]
    assert find_duplicates(regs) == ["R2"]


def test_different_timezone_offsets():
    """10:03+07:00 = 03:03 UTC, 10:05+08:00 = 02:05 UTC. 58 minutes apart, not duplicate."""
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:05:00+08:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:03:00+07:00"},
    ]
    assert find_duplicates(regs) == []


def test_different_timezone_offsets_actually_close():
    """09:00+07:00 = 02:00 UTC, 10:03+08:00 = 02:03 UTC. 3 minutes apart, IS duplicate."""
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T09:00:00+07:00"},
        {"registration_id": "R2", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:03:00+08:00"},
    ]
    assert find_duplicates(regs) == ["R2"]


def test_multiple_patients_interleaved():
    regs = [
        {"registration_id": "R1", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:00:00+08:00"},
        {"registration_id": "R2", "patient_id": "P200", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:01:00+08:00"},
        {"registration_id": "R3", "patient_id": "P100", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:02:00+08:00"},
        {"registration_id": "R4", "patient_id": "P200", "puskesmas_id": "PKM-001", "registered_at": "2026-03-15T10:03:00+08:00"},
    ]
    result = find_duplicates(regs)
    assert sorted(result) == ["R3", "R4"]
