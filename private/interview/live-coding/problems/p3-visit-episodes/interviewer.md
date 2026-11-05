# P3: Visit Episodes - Interviewer Notes

## Intentional Ambiguities

### 1. Exactly 14 days

Is exactly 14 days a new episode?
- **Answer if asked:** No, 14 days is the same episode. Only **more than 14 days** starts a new one.

### 2. Same-day visits

Two visits on the same date for the same patient - one visit or two?
- **Answer if asked:** Count both in `visit_count`. They are separate visits that happen to be on the same day.

## Edge Cases (all must be in tests)

1. **Unsorted input** - visits not in chronological order, multiple patients interleaved
2. **Single visit** - one episode with visit_count = 1, start_date == end_date
3. **Exactly 14 days gap** - same episode (not > 14)
4. **Exactly 15 days gap** - new episode (> 14)
5. **Same-day visits** - count both, one episode
6. **Multiple patients** - episodes are per-patient
7. **Gap crossing month boundary** - Jan 25 to Feb 10 (16 days, new episode)
8. **Empty input** - return empty list

## What a Strong Candidate Does

- Asks about the 14-day boundary and same-day visits
- Says "I'll group by patient, sort by date, then scan for gaps > 14 days" before coding
- Mentions O(n log n) for the sort
- Handles single-visit episodes and same-day visits
- Tests with the given example, then adds a boundary case (exactly 14 vs 15)

## Common Mistakes

- Forgetting to sort by date
- Off-by-one: using >= 14 instead of > 14 (or vice versa)
- Comparing date strings instead of parsing to dates (works for YYYY-MM-DD but candidate should know why)
- Not grouping by patient first
- Forgetting that start_date == end_date for single-visit episodes
- Counting same-day visits as 1

## Hint Ladder

1. **Gentle nudge:** "What if visits for different patients are mixed together?"
2. **Specific pointer:** "Try grouping by patient first, then sorting each group by date."
3. **Nearly the approach:** "For each patient, sort their visits by date, then walk through comparing each visit to the previous one. If the gap is > 14 days, start a new episode."

## Twist

> "A late visit arrives that falls between two existing episodes and might join them. How would you update the result without recomputing everything?"

**Good answers:**
- Find which episode(s) the new visit is adjacent to (within 14 days of the end of one episode and/or start of another)
- If it bridges two episodes, merge them
- If it extends one, update that episode's dates and count
- If it's isolated, insert a new single-visit episode
- Mention that a sorted data structure (like a sorted list of episodes) would make this efficient

**Weak answers:**
- "Just recompute everything" (correct but misses the point)
- No mention of the merge case

## Time Guide

- 0:00-0:05 - Read, clarifying questions
- 0:05-0:10 - Explain approach
- 0:10-0:25 - Code and test
- 0:25-0:30 - Twist discussion
