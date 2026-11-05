# Follow-Up Call Interview Guide (45 minutes)

## Before the Call

- Read their `REVIEW.md`, `DESIGN.md` or `ASSUMPTIONS.md`, and `AI_USAGE.md`
- Run detection tests against their Task 1 fixes
- If Task 2: run the grading harness against their endpoint
- If Task 3: compare their numbers against ground truth
- Note 2-3 specific questions based on their submission

---

## Task 1: Clinic Sync Service (~15 minutes)

### Prioritization Deep-Dive (5 min)

"Walk me through your top 3. Why is [their #1] ranked above [their #3]?"

**Listen for:** Concrete impact reasoning, not abstract severity labels. "This causes data loss" vs "This is a high-severity bug."

If they ranked a style issue highly:
"If this service goes live Monday and you can only fix one thing this weekend, which one and why?"

### Code Understanding (5 min)

Pick a random line in one of their fixes:
"What does this line do, and what happens if you remove it?"

Pick a line they didn't fix:
"You noticed [defect X] but didn't fix it. What's the risk of shipping with it?"

### Scenario (5 min)

"It's Thursday evening. The service has been running at 40 clinics for a week. Finance calls and says their monthly totals are off by 12%. Where do you start investigating?"

**Listen for:** Structured debugging approach. Check logs → check claim API for duplicates → check for failed syncs marked as success → timezone issue on cross-facility reports.

**Notes:**
_____________________________________
_____________________________________
_____________________________________

---

## Task 2: Offline-First Sync (~20 minutes, if chosen)

### Live Constraints (10 min)

Present one at a time, give them 2-3 minutes each:

1. "The claim API goes down for 6 hours. What does the health worker see on their phone? What happens when it comes back?"

   **Listen for:** Offline-first design means the health worker sees nothing different. Data queues locally. On reconnect, batches sync with idempotency. No data loss.

2. "One Puskesmas now has 10x the volume — 500 visits per day instead of 50. What breaks first in your design?"

   **Listen for:** Batch size limits, sync duration, database growth, stock contention. Practical scaling concerns, not theoretical.

3. "A kader (community health worker) shares a phone with a colleague. Both enter data under different accounts. What happens?"

   **Listen for:** Device ID vs user ID distinction. Data attribution. Audit trail concerns.

### Implementation Questions (5 min)

"Show me your idempotency implementation. What happens if the server crashes between accepting a record and sending the response?"

"How does your review queue work? Who sees it, and what can they do?"

### Scope Challenge (5 min)

"Your MVP list says you wouldn't build [X]. The product manager says it's essential. How do you push back, or do you?"

**Notes:**
_____________________________________
_____________________________________
_____________________________________

---

## Task 3: Dinkes Report (~20 minutes, if chosen)

### Live Change on Screen Share (10 min)

"Dinkes says general clinic and dental clinic on the same day count as **1 visit**, not 2. Can you modify your query now while sharing your screen?"

**Listen for:** Composure under pressure. Can they modify a GROUP BY or add a DISTINCT? Do they test the change? How long does it take?

Follow-up: "How did that change affect your numbers? By how much?"

### Verification (5 min)

"How would you check this number is right before it goes on the dashboard?"

**Listen for:** Cross-validation strategies. Compare with paper records. Sample audit. Check boundary cases (month transitions, facility splits). Not just "run the query again."

### Anomaly Deep-Dive (5 min)

Pick an anomaly they found:
"You found [anomaly X]. How did you discover it, and how confident are you in the count?"

Pick an anomaly they missed:
"Did you notice anything about patients who share the same NIK but have very different birth dates?"

**Notes:**
_____________________________________
_____________________________________
_____________________________________

---

## Skipped Task (~5 minutes, verbal only)

### If they skipped Task 2:

"Quick one — no preparation expected. If you had to make sure a sale syncs exactly once from an offline phone, what's your one-sentence approach?"

**Listen for:** Client-generated ID + server dedup. Not "use a queue."

### If they skipped Task 3:

"Quick one — if you had to count unique patients and some share a placeholder NIK like all zeros, what would you do?"

**Listen for:** Awareness that DISTINCT NIK doesn't work. Patient ID or name+DOB-based counting.

**Note:** This is a light signal. Don't penalize heavily — they weren't asked to prepare for it.

**Notes:**
_____________________________________

---

## AI Usage (~5 minutes)

"What did the AI get wrong that you caught?"

**Listen for:** Specific examples, not vague disclaimers. "It suggested mocking the database for tests, but I wanted integration tests because..." is strong. "I reviewed everything the AI produced" is weak.

"Was there something you tried to get the AI to do but gave up on?"

"If you could only use AI for one part of this assessment, which part and why?"

**Notes:**
_____________________________________
_____________________________________

---

## Scoring Summary

| Area | Score (1-5) | Notes |
|------|-------------|-------|
| Code ownership / can explain their work | | |
| Adaptability / handles live changes | | |
| Depth of understanding | | |
| Honesty about limitations | | |
| AI awareness and judgment | | |
| Communication clarity | | |

**Overall call impression:**
_____________________________________
_____________________________________
