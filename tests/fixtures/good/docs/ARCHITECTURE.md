# Architecture

## Overview
Hono serves JSON and HTML; Drizzle stores habits and check-ins in SQLite.

```mermaid
flowchart LR
  browser[Browser] --> routes[Hono routes] --> queries[Queries] --> db[(SQLite)]
```

Imports flow: `src/routes.ts` → `src/streaks.ts` and `src/db/queries.ts`; nothing imports `src/routes.ts`.

## Modules
| Path | Owns |
| --- | --- |
| `src/routes.ts` | HTTP handlers |
| `src/db/queries.ts` | All database reads and writes |
| `src/streaks.ts` | Streak and calendar calculations over day strings |

## Invariants
- I01 A habit has at most one check-in per local day — enforced by `tests/queries.test.ts`

## Glossary
- **Day**: a `YYYY-MM-DD` string in the user's zone, never a timestamp.

## Specs
- [streaks](specs/streaks.md) — current streak and the 30-day calendar
