# Live Coding Session - Interviewer Guide

## Overview

30-minute live coding session during the follow-up interview. One problem per candidate, done over screen share. No AI tools allowed.

**Purpose:** See how candidates think on their own. The take-home already shows how they work *with* AI.

## Setup

1. Candidate shares their screen
2. They use their own editor, any language they choose
3. They may use official language documentation (docs, man pages)
4. **No AI assistants, no AI-powered autocomplete** - tell them at the start

## Opening Script

> "For the next 30 minutes, we'll work through a small coding problem together. Please think out loud - I want to understand your reasoning. Questions are welcome, especially about things the problem doesn't specify. You can use any language and your own editor. Please turn off any AI assistants or AI-powered autocomplete for this part."

## Picking the Problem

Rotate problems across candidates to prevent answer-sharing:

| Problem | Topic |
|---------|-------|
| P1 | Duplicate registrations (time-window dedup) |
| P2 | Medicine stock timeline (event replay) |
| P3 | Visit episodes (gap-based grouping) |

Record which problem each candidate gets. If two candidates know each other, give them different problems. Use remaining problems as backups if a candidate finishes early.

All three problems are similar difficulty (easy-medium). Pick based on rotation, not candidate profile.

## Session Flow

| Time | What Happens |
|------|-------------|
| 0:00-0:05 | Share the problem statement. Let them read. Answer clarifying questions. |
| 0:05-0:10 | Ask: "Before you start coding, can you walk me through your approach?" |
| 0:10-0:25 | Coding. Give hints if stuck (see hint ladder in each `interviewer.md`). |
| 0:25-0:30 | The twist question (verbal only, no code needed). |

## How to Stay Neutral

- **Don't confirm answers mid-way.** If they ask "Is this right?", say "Let's keep going and test it."
- **Don't rescue too early.** Give them at least 3-4 minutes of being stuck before offering a hint.
- **Don't react to bugs.** Let them find bugs through their own testing.
- Use the hint ladder in order. Each hint costs points on the scoring sheet.

## Fairness Notes

- Nerves are normal. Score reasoning over speed.
- Allow pseudocode if they freeze on syntax.
- A candidate who doesn't finish but reasons well can still score "meets expectations."
- If they choose an unfamiliar language (e.g., trying Python when they normally use Go), don't penalize syntax struggles.
- Time pressure is part of the test, but understanding is more important than completion.

## After the Session

Fill in `scoring-sheet.md` immediately while the session is fresh.
