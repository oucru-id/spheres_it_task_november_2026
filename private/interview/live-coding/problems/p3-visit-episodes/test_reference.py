from reference import find_episodes


def test_basic_example():
    visits = [
        {"patient_id": "P1", "visit_date": "2026-01-01"},
        {"patient_id": "P1", "visit_date": "2026-01-10"},
        {"patient_id": "P1", "visit_date": "2026-01-30"},
        {"patient_id": "P1", "visit_date": "2026-02-05"},
    ]
    result = find_episodes(visits)
    assert len(result) == 2
    assert result[0] == {"patient_id": "P1", "start_date": "2026-01-01", "end_date": "2026-01-10", "visit_count": 2}
    assert result[1] == {"patient_id": "P1", "start_date": "2026-01-30", "end_date": "2026-02-05", "visit_count": 2}


def test_empty_input():
    assert find_episodes([]) == []


def test_single_visit():
    visits = [{"patient_id": "P1", "visit_date": "2026-01-15"}]
    result = find_episodes(visits)
    assert result == [{"patient_id": "P1", "start_date": "2026-01-15", "end_date": "2026-01-15", "visit_count": 1}]


def test_exactly_14_days_same_episode():
    visits = [
        {"patient_id": "P1", "visit_date": "2026-01-01"},
        {"patient_id": "P1", "visit_date": "2026-01-15"},
    ]
    result = find_episodes(visits)
    assert len(result) == 1
    assert result[0]["visit_count"] == 2


def test_exactly_15_days_new_episode():
    visits = [
        {"patient_id": "P1", "visit_date": "2026-01-01"},
        {"patient_id": "P1", "visit_date": "2026-01-16"},
    ]
    result = find_episodes(visits)
    assert len(result) == 2
    assert result[0]["visit_count"] == 1
    assert result[1]["visit_count"] == 1


def test_same_day_visits_count_both():
    visits = [
        {"patient_id": "P1", "visit_date": "2026-01-10"},
        {"patient_id": "P1", "visit_date": "2026-01-10"},
    ]
    result = find_episodes(visits)
    assert len(result) == 1
    assert result[0]["visit_count"] == 2
    assert result[0]["start_date"] == "2026-01-10"
    assert result[0]["end_date"] == "2026-01-10"


def test_unsorted_input():
    visits = [
        {"patient_id": "P1", "visit_date": "2026-01-30"},
        {"patient_id": "P1", "visit_date": "2026-01-01"},
        {"patient_id": "P1", "visit_date": "2026-01-10"},
    ]
    result = find_episodes(visits)
    assert len(result) == 2
    assert result[0] == {"patient_id": "P1", "start_date": "2026-01-01", "end_date": "2026-01-10", "visit_count": 2}
    assert result[1] == {"patient_id": "P1", "start_date": "2026-01-30", "end_date": "2026-01-30", "visit_count": 1}


def test_multiple_patients():
    visits = [
        {"patient_id": "P1", "visit_date": "2026-01-01"},
        {"patient_id": "P2", "visit_date": "2026-01-02"},
        {"patient_id": "P1", "visit_date": "2026-01-05"},
        {"patient_id": "P2", "visit_date": "2026-02-01"},
    ]
    result = find_episodes(visits)
    p1_eps = [e for e in result if e["patient_id"] == "P1"]
    p2_eps = [e for e in result if e["patient_id"] == "P2"]
    assert len(p1_eps) == 1
    assert p1_eps[0]["visit_count"] == 2
    assert len(p2_eps) == 2
    assert p2_eps[0]["visit_count"] == 1
    assert p2_eps[1]["visit_count"] == 1


def test_gap_crossing_month_boundary():
    visits = [
        {"patient_id": "P1", "visit_date": "2026-01-25"},
        {"patient_id": "P1", "visit_date": "2026-02-10"},
    ]
    # 16 days apart, new episode
    result = find_episodes(visits)
    assert len(result) == 2


def test_gap_crossing_year_boundary():
    visits = [
        {"patient_id": "P1", "visit_date": "2025-12-28"},
        {"patient_id": "P1", "visit_date": "2026-01-05"},
    ]
    # 8 days apart, same episode
    result = find_episodes(visits)
    assert len(result) == 1
    assert result[0]["visit_count"] == 2


def test_many_visits_one_episode():
    visits = [
        {"patient_id": "P1", "visit_date": f"2026-01-{d:02d}"}
        for d in range(1, 15)
    ]
    result = find_episodes(visits)
    assert len(result) == 1
    assert result[0]["visit_count"] == 14
