# Task 3: Clarifying Question Quality Guide

## Strong Questions (change the answer)

- "When a patient sees both the general and dental clinic on the same day, does Dinkes count that as 1 visit or 2 for the dashboard?"
- "Puskesmas Gunungsari appears under two different names/IDs in the data. Should we treat these as the same facility?"
- "Some registrations are marked 'cancelled' or 'no_show' but still have visit records. Should these be included in the count?"
- "About 300 patients have placeholder NIK 0000000000000000. How should we count unique patients when the NIK isn't reliable?"

## Acceptable Questions (show awareness, clarify scope)

- "Should the report show calendar months in local time (WIB/WITA) or a consistent timezone?"
- "Are implausible records (birth dates in the future or age > 120) known data entry errors we should exclude?"
- "Should infants registered under their mother's NIK be counted as separate patients?"

## Weak Questions (don't change anything meaningful)

- "What format should the output table be in?" (Focus on the data, not the format)
- "Should I include a total row?" (Trivial formatting)
- "How many decimal places for percentages?" (Not asked for percentages)

## Red Flags

- "Is the data clean?" (Shows they didn't look)
- "Should I use SQL or Python?" (We said either is fine)
- No question at all, combined with naive results (suggests they didn't find the anomalies)
- A question that reveals they used AI to scan the data without understanding it: "I noticed several data quality issues including duplicates, missing values, and inconsistencies. Which ones should I prioritize?" (Vague, doesn't name specific problems)
