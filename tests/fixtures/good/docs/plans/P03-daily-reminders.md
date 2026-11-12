# P03 Daily reminders

Format: 4
Kind: feature
Approved: 2026-10-30 T01–T02
Depends on: P02
Touches: `src/reminders.ts` (new), `src/routes.ts`, `src/db/`
Read: streaks, D002, I01

## Goal
The user sets a daily reminder time per habit and sees a banner when it is due and the habit isn't checked in.

In: one reminder time per habit, an in-page banner.
Out: email and push notifications.

## Requirements
C1. A reminder time is `HH:MM` in the user's zone; anything else → 400 `invalid_time`.
C2. The banner shows from the reminder time until the habit is checked in that day, the same day streaks R1 counts.
C3. [streaks new] A habit with a reminder shows its next reminder time beside the streak.
C4. Saving the same time twice leaves one reminder.

## Design
    PUT /habits/:id/reminder { time: "HH:MM" } → 204 | 400 { error: "invalid_time" } | 404

| Question | Decision | Rejected | Why |
| --- | --- | --- | --- |
| Scheduler | In-process timer (D002) | Job queue | One process and a few jobs a day |

## Tasks
- [x] P03-T01 Store reminder times
  Done when: C1 and C4 hold; I01 still holds.
- [ ] P03-T02 Show the reminder banner
  Done when: C2 and C3 hold, with tests at the day boundary.
- [ ] P03-T03 Add the reminder settings form
  Done when: the form saves through the endpoint, and shows loading and the 400 error.

## Acceptance
Auto:
- `pnpm vitest run` → pass
Manual:
- Set a reminder one minute ahead → the banner appears, and checking in removes it

## Log

### P03-T02 · blocked · 2026-10-31
Question: C2 needs the user's zone on the server, but D001 keeps zones on the client.
Options: A) the client sends its zone with each request B) store a zone per user. Recommend A.

### P03-T02 · cleared · 2026-10-31
Resolution: A. The client sends its zone; Design is unchanged.
