from collections import defaultdict


def find_first_negative(starting_stock: dict, events: list[dict]) -> dict:
    """Return the first timestamp each medicine's stock goes below zero."""
    grouped = defaultdict(list)
    for e in events:
        grouped[e["medicine_id"]].append(e)

    result = {}

    for med_id, med_events in grouped.items():
        med_events.sort(key=lambda e: (e["timestamp"], 0 if e["type"] == "in" else 1))

        stock = starting_stock.get(med_id, 0)

        for e in med_events:
            if e["type"] == "in":
                stock += e["quantity"]
            else:
                stock -= e["quantity"]

            if stock < 0:
                result[med_id] = e["timestamp"]
                break

    return result
