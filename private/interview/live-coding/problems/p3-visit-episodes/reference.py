from collections import defaultdict
from datetime import date, timedelta


def find_episodes(visits: list[dict]) -> list[dict]:
    """Group visits into episodes. New episode starts after > 14 day gap."""
    by_patient = defaultdict(list)
    for v in visits:
        by_patient[v["patient_id"]].append(v["visit_date"])

    episodes = []

    for patient_id in sorted(by_patient):
        dates = sorted(set_or_list(by_patient[patient_id]))

        start = dates[0]
        prev = dates[0]
        count = 1

        for d in dates[1:]:
            gap = (parse_date(d) - parse_date(prev)).days
            if gap > 14:
                episodes.append({
                    "patient_id": patient_id,
                    "start_date": start,
                    "end_date": prev,
                    "visit_count": count,
                })
                start = d
                count = 1
            else:
                count += 1
            prev = d

        episodes.append({
            "patient_id": patient_id,
            "start_date": start,
            "end_date": prev,
            "visit_count": count,
        })

    return episodes


def set_or_list(dates):
    """Keep all dates (same-day visits count separately)."""
    return sorted(dates)


def parse_date(d: str) -> date:
    return date.fromisoformat(d)
