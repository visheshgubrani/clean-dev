# Lean code

Simple code is the cheapest code to plan, build, review, and change. The rules below are expanded versions of the ten in `SKILL.md`. Each one comes from a pattern that kept recurring in real apps built with this workflow.
- **Builders** apply them to every internal choice they make.
- **Planners** apply them when placing owners and seams.
- **Reviewers** check every diff against them.

## The complexity ladder

Move up one step only when the condition for that step is true now. Builders take steps 1–4 themselves. Step 4 is logged under `Choices:`, and the new module is added to AGENTS.md owners. Steps 5–6, or any step that changes a seam, need a row in the plan's Choices table.

1. **Inline code.** This is the default.
2. **Private function** in the same file, once the code needs a name or appears twice there.
3. **Function in the owning module** (see "Where things live"), when a second file needs it.
4. **Shared module**, when a second module would otherwise copy it. Add it to AGENTS.md "Where things live".
5. **Interface, base class, or registry**, once a second real implementation exists. A test fake counts.
6. **Package or service**, only for a separate deploy target or an outside consumer.

## Rules

### 1. One owner per concern

AGENTS.md "Where things live" names one module each for config/env, logging, errors, database access, the API/HTTP client, dates/time, text formatting, validation schemas, and shared types. Use that module, and add missing helpers to it.

- **Seen:** `clip()` defined three times, `readJson`/`isRecord` seven times, date formatting re-implemented in six components despite a file that called itself "the one place", and `_fmt` in four modules.
- **Do:** before adding a helper, search the owners in AGENTS.md and run `grep -rn "<likely name or concept>"`. Builders: when you find a second copy inside your phase's scope, move it to the owner and update every caller. Outside your scope, note it in the log for the planner.

### 2. Size is a prompt, not a cap

A source file past ~400 lines or a function past ~80 is a reason to ask whether it holds a second responsibility. It is not a number to hit. Generated, vendored, data, lock, and migration files don't count.

- **Seen:**
  - One workspace component took most of the features (touched in 10 of 22 commits).
  - Profiling modules reached 2,480 lines, and one function ran to about 330 lines.
  - Under a hard cap, a builder compressed formatting to land a file at 393 lines; the file got harder to read and no simpler.
- **Do:**
  - Put a new responsibility in a new module, not into the biggest existing file.
  - When a change would grow a large file by another responsibility, split along that responsibility first, with no behavior change, as part of the same phase.
  - Never reformat to fit a number.

### 3. Variants share one core; old paths die

- **Seen:**
  - a second experiment pipeline copied from the first, with seven duplicated private functions;
  - two upload routes with identical helpers;
  - v1 and v2 transcoding pipelines both kept alive behind a flag;
  - a modal replaced by a page but still edited for weeks.
- **Do:** follow the Patterns exemplar and pass the differences in as data or a small parameter. The phase that replaces a path also deletes it, along with its flag and tests.

### 4. No re-export shims or aliases inside an app

- **Seen:** after helpers moved to `llm/`, the old `mail/` files kept two-line re-exports and renamed aliases that nothing needed.
- **Do:** when you move something, update every import in the same task. Shims are only for published packages with outside consumers.

### 5. Validate at trust boundaries only

The trust boundaries are environment variables, request input, external API responses, model output, and files read from disk. Parse them once with the project's schema library, then trust the types.

- **Seen:** 55 hand-written guards re-checking the app's own API responses, hand-rolled `_as_int`/`_require_known_keys` in two parallel contract modules, and 28–30 custom error classes per app.
- **Do:** use one schema per boundary, with its type inferred from the schema. Add a custom error class only when some caller catches that specific class. Otherwise throw the standard error with context.

### 6. No interface before two implementations

- **Seen:**
  - an abstract broker base class with one broker;
  - a Strategy Protocol plus a base class plus a registry for two strategies.
- **Good examples:**
  - a runner seam with a real mock and a real engine that fails loudly when misconfigured;
  - a browser driver interface with Playwright and a test fake.
- **Do:** write the concrete function. Introduce the seam in the task that adds the second implementation.

### 7. Export only what is imported; delete dead code; no scaffolding

- **Seen:** about 1,000 lines of unused components in one app, 90 exports referenced nowhere, and an untouched framework template kept "for later".
- **Do:**
  - Keep a symbol private until another file imports it.
  - The task that makes code unused deletes it.
  - Don't create folders, stubs, flags, or config for future phases.

### 8. Comments explain why

- **Seen:** 143 references to phases, units, and decision IDs in source, plus a package docstring used as a status log.
- **Do:** comment a non-obvious reason, constraint, or invariant in plain words. The commit subject carries the task ID. Docs carry status and history.

### 9. One data-access layer; thin edges

- **Seen:**
  - **Good:** in one app no file outside `lib/db` imports the ORM, and its routes stay under 120 lines.
  - **Bad:** in another, 50 files import the ORM directly, and route files run 600–1,000 lines with their own queries.
- **Do:**
  - Queries live in the data-access module.
  - Routes, handlers, CLI scripts, and components parse input, call one function, and map the result.
  - The UI has one API client, and one loader hook per resource.

### 10. Pure core, I/O at the edges, one-way imports

- **Seen (good):**
  - cost, fill, and metric calculations as pure modules tested directly;
  - schedulers and planners as pure functions;
  - research code importing the engine, never the reverse.
- **Do:** put decisions and calculations in functions that take data and return data. Keep network, database, filesystem, and clock access in thin adapters. Test the pure functions first.

## Tests

- **Test behavior at the public function or endpoint.** Don't mirror the implementation.
- **Put each failure case from the requirements in a test:** timeouts, duplicates, invalid input, boundaries.
- **Every bug fix starts with a failing regression test.**
- **Fakes:** use one shared fake per external boundary. Don't add a mocking library. The language's built-in tools, such as `unittest.mock` or `vi.fn`, are fine.
- **Keep fast tests separate from tests that need real services**, so the Fast check stays fast.

## Dependencies and config

- **New dependencies need approval through a plan's Choices row,** naming the current need and the alternative of writing about 30 lines yourself. Builders block rather than add one.
- **Read the environment in the config owner only.**
- **Add a config option only when the user needs to change that value now.**
