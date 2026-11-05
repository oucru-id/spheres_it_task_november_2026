# P1: Duplicate Registrations - Interviewer Notes

## Intentional Ambiguities

These are deliberately left unstated. Note whether the candidate asks about them.

### 1. Chaining

Registrations at 10:00, 10:04, and 10:08. Is 10:08 a duplicate?
- It's within 5 minutes of 10:04 but not of 10:00.
- **Answer if asked:** Compare against the last *kept* registration. So 10:04 is a duplicate of 10:00 (kept). Then 10:08 is compared against 10:00 (the last kept), which is 8 minutes - not a duplicate.
- **Accept either rule** if the candidate states it clearly and implements it consistently.

### 2. Exactly 5 minutes

Is exactly 5 minutes (300 seconds) a duplicate?
- **Answer:** Yes, <= 5 minutes is a duplicate.

### 3. Which copy is kept

When a duplicate pair is found, which one is the duplicate?
- **Answer:** Keep the earliest, mark the later one as duplicate.

## Edge Cases (all must be in tests)

1. **Unsorted input** - registrations not in chronological order
2. **Null patient_id** - never treated as duplicate, even if same puskesmas/time
3. **Different timezone offsets** - `+07:00` and `+08:00` that are actually close in absolute time (e.g., `10:03:00+07:00` and `10:05:00+08:00` are 62 minutes apart, NOT 2 minutes)
4. **Crossing midnight** - `23:58:00` and `00:01:00` next day, 3 minutes apart
5. **Same patient, different puskesmas** - not a duplicate
6. **Empty input** - return empty list
7. **Single registration** - return empty list

## What a Strong Candidate Does

- Asks about chaining, boundary (exactly 5 min), and which copy to keep
- Says "I'll sort by patient+puskesmas+time, then scan" before coding
- Mentions O(n log n) for sorting approach
- Handles null patient_id explicitly
- Tests with the given example, then adds an edge case (midnight crossing or timezone)

## Common Mistakes

- Forgetting to sort - compares adjacent rows in input order
- Comparing timestamps as strings (breaks across timezones and midnight)
- Off-by-one on 5-minute boundary (using < instead of <=)
- O(n^2) nested loop comparing every pair - works but slow
- Not handling null patient_id (treats null == null as a match)

## Hint Ladder

1. **Gentle nudge:** "What if the input isn't sorted by time?"
2. **Specific pointer:** "Try grouping by patient and puskesmas, then sorting by time within each group."
3. **Nearly the approach:** "Sort, then for each group, walk through and compare each registration against the last one you kept."

## Twist

> "The list is 50 million rows and doesn't fit in memory. How would you do this?"

**Good answers:**
- Sort on disk (external sort) by (patient_id, puskesmas_id, registered_at), then stream through
- Partition by patient_id or (patient_id, puskesmas_id), process each partition independently
- Push into a database: `GROUP BY patient_id, puskesmas_id` with window functions (`LAG`)
- MapReduce: key by (patient_id, puskesmas_id), reduce with sorted scan

**Weak answers:**
- "Use more RAM" or "use Spark" without explaining the partitioning logic

## Time Guide

- 0:00-0:05 - Read, clarifying questions
- 0:05-0:10 - Explain approach
- 0:10-0:25 - Code and test
- 0:25-0:30 - Twist discussion
