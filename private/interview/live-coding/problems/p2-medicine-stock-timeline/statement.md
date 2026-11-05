# Medicine Stock Timeline

A Puskesmas (community health clinic) tracks medicine stock. Deliveries add stock, dispensing removes stock. Events may arrive **out of order** (e.g., a phone that was offline sends data late).

## Problem

You are given:
1. A dictionary of **starting stock** for each medicine: `{"MED-001": 100, "MED-002": 50}`
2. A list of **events**, each with:
   - `medicine_id` (string)
   - `type` (`"in"` for delivery, `"out"` for dispensing)
   - `quantity` (integer, always > 0)
   - `timestamp` (ISO 8601 string, e.g. `"2026-03-15T10:30:00"`)

Events are **not necessarily in order**.

Return a dictionary mapping each medicine to the **first timestamp** at which its stock goes **below zero**. Only include medicines that actually go negative.

## Example

```
starting_stock = {"MED-001": 10}

events = [
  {"medicine_id": "MED-001", "type": "out", "quantity": 8, "timestamp": "2026-03-15T09:00:00"},
  {"medicine_id": "MED-001", "type": "out", "quantity": 5, "timestamp": "2026-03-15T10:00:00"},
  {"medicine_id": "MED-001", "type": "in",  "quantity": 20, "timestamp": "2026-03-15T11:00:00"}
]
```

Output:
```
{"MED-001": "2026-03-15T10:00:00"}
```

After the first dispensing: 10 - 8 = 2. After the second: 2 - 5 = -3 (first time negative). The delivery at 11:00 brings it back to 17, but we only care about the first time it went negative.

## Your Task

Write a function that takes the starting stock and event list and returns the result.
