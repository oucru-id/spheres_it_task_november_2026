# P2: Medicine Stock Timeline - Interviewer Notes

## Intentional Ambiguities

### 1. Same-timestamp tie-breaking

Delivery and dispensing at the same timestamp - which goes first?
- **Answer if asked:** Deliveries (`in`) first, then dispensing (`out`).

### 2. Unknown medicine

An event references a medicine not in starting_stock.
- **Answer if asked:** Treat starting stock as 0.

## Edge Cases (all must be in tests)

1. **Unsorted events** - events not in chronological order
2. **Ties at same timestamp** - delivery and dispensing at same time (delivery first)
3. **Stock exactly 0** - not negative, do not include
4. **Goes negative, recovers, goes negative again** - return only the first time
5. **Quantity 0** - technically valid but doesn't change stock (problem says always > 0, but test anyway)
6. **Empty input** - empty events list, return empty dict
7. **Medicine with no events** - not included in result (never goes negative from starting stock alone)
8. **Medicine not in starting_stock** - starts at 0

## What a Strong Candidate Does

- Asks about tie-breaking and unknown medicines
- Says "I'll group by medicine, sort events by time, then simulate" before coding
- Mentions O(n log n) per medicine for sorting
- Handles the "first time only" requirement cleanly (break or flag)
- Tests with the given example, then tries an edge case

## Common Mistakes

- Forgetting to sort events by timestamp
- Not handling tie-breaking (delivery before dispensing at same time)
- Returning the last time stock goes negative instead of the first
- Not grouping by medicine (processing all events in one pass without separation)
- Treating 0 as negative

## Hint Ladder

1. **Gentle nudge:** "What order do you process the events in?"
2. **Specific pointer:** "Try grouping events by medicine, then sorting each group by timestamp."
3. **Nearly the approach:** "For each medicine, sort its events, walk through them keeping a running total, and stop when it goes below zero."

## Twist

> "Now return every period when stock was negative, with start and end timestamps."

**Good answers:**
- Track when stock goes negative (start) and when it recovers to >= 0 (end)
- Handle the case where stock is still negative at the end (open-ended period)
- Return a list of `{start, end}` per medicine

**Alternative twist:**
> "Events arrive one at a time from phones that were offline, so a late event can change past results. What changes?"

**Good answers:**
- Need to re-simulate from the point of the late event
- Could maintain a sorted event log and replay from insertion point
- Mention that results become "provisional" until all devices sync

## Time Guide

- 0:00-0:05 - Read, clarifying questions
- 0:05-0:10 - Explain approach
- 0:10-0:25 - Code and test
- 0:25-0:30 - Twist discussion
