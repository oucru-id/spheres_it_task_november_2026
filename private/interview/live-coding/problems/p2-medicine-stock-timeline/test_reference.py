from reference import find_first_negative


def test_basic_example():
    starting = {"MED-001": 10}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 8, "timestamp": "2026-03-15T09:00:00"},
        {"medicine_id": "MED-001", "type": "out", "quantity": 5, "timestamp": "2026-03-15T10:00:00"},
        {"medicine_id": "MED-001", "type": "in",  "quantity": 20, "timestamp": "2026-03-15T11:00:00"},
    ]
    assert find_first_negative(starting, events) == {"MED-001": "2026-03-15T10:00:00"}


def test_empty_events():
    assert find_first_negative({"MED-001": 10}, []) == {}


def test_empty_starting_stock_and_events():
    assert find_first_negative({}, []) == {}


def test_never_goes_negative():
    starting = {"MED-001": 100}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 10, "timestamp": "2026-03-15T09:00:00"},
        {"medicine_id": "MED-001", "type": "out", "quantity": 10, "timestamp": "2026-03-15T10:00:00"},
    ]
    assert find_first_negative(starting, events) == {}


def test_stock_exactly_zero_not_negative():
    starting = {"MED-001": 10}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 10, "timestamp": "2026-03-15T09:00:00"},
    ]
    assert find_first_negative(starting, events) == {}


def test_unsorted_events():
    starting = {"MED-001": 10}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 5, "timestamp": "2026-03-15T10:00:00"},
        {"medicine_id": "MED-001", "type": "out", "quantity": 8, "timestamp": "2026-03-15T09:00:00"},
        {"medicine_id": "MED-001", "type": "in",  "quantity": 20, "timestamp": "2026-03-15T11:00:00"},
    ]
    assert find_first_negative(starting, events) == {"MED-001": "2026-03-15T10:00:00"}


def test_same_timestamp_delivery_before_dispensing():
    starting = {"MED-001": 0}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 5, "timestamp": "2026-03-15T10:00:00"},
        {"medicine_id": "MED-001", "type": "in",  "quantity": 10, "timestamp": "2026-03-15T10:00:00"},
    ]
    # Delivery first: 0 + 10 = 10, then out: 10 - 5 = 5. Never negative.
    assert find_first_negative(starting, events) == {}


def test_same_timestamp_goes_negative_without_delivery():
    starting = {"MED-001": 3}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 5, "timestamp": "2026-03-15T10:00:00"},
    ]
    assert find_first_negative(starting, events) == {"MED-001": "2026-03-15T10:00:00"}


def test_goes_negative_recovers_goes_negative_again():
    starting = {"MED-001": 5}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 8,  "timestamp": "2026-03-15T09:00:00"},
        {"medicine_id": "MED-001", "type": "in",  "quantity": 20, "timestamp": "2026-03-15T10:00:00"},
        {"medicine_id": "MED-001", "type": "out", "quantity": 25, "timestamp": "2026-03-15T11:00:00"},
    ]
    # First time negative: 09:00 (5 - 8 = -3)
    assert find_first_negative(starting, events) == {"MED-001": "2026-03-15T09:00:00"}


def test_unknown_medicine_starts_at_zero():
    starting = {}
    events = [
        {"medicine_id": "MED-999", "type": "out", "quantity": 1, "timestamp": "2026-03-15T09:00:00"},
    ]
    assert find_first_negative(starting, events) == {"MED-999": "2026-03-15T09:00:00"}


def test_multiple_medicines():
    starting = {"MED-001": 10, "MED-002": 5}
    events = [
        {"medicine_id": "MED-001", "type": "out", "quantity": 3, "timestamp": "2026-03-15T09:00:00"},
        {"medicine_id": "MED-002", "type": "out", "quantity": 8, "timestamp": "2026-03-15T09:30:00"},
        {"medicine_id": "MED-001", "type": "out", "quantity": 3, "timestamp": "2026-03-15T10:00:00"},
    ]
    # MED-001: 10 - 3 - 3 = 4. Never negative.
    # MED-002: 5 - 8 = -3. Negative at 09:30.
    assert find_first_negative(starting, events) == {"MED-002": "2026-03-15T09:30:00"}


def test_medicine_with_no_events():
    starting = {"MED-001": 10}
    events = []
    assert find_first_negative(starting, events) == {}
