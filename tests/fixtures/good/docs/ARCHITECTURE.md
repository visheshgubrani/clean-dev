# Architecture

## Overview
Hono serves JSON and HTML; Drizzle stores habits and check-ins in SQLite.
Data flow: `src/routes.ts` → `src/db/queries.ts` → SQLite

## Invariants
- I01 A habit has at most one check-in per local day — enforced by `tests/queries.test.ts`
