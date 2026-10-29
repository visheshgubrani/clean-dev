# Plan example: one phase, two depths

This is one real phase written two ways. Use it to calibrate how much a plan should say.

**The phase:** a video pipeline's steps run only as Modal functions. They become plain Python that one local process can also run, and Modal behaves exactly as before.

The v2 plan ran to 353 lines with six cards. The v3 plan below is about 100 lines. Both constrain the same things: compatibility, security, failure behavior, and the two seams later phases build on. Only v2 also wrote the code in prose.

## Before (v2, excerpt)

One requirement and part of one card:

```markdown
C2. `utils/cmd.py`:

    def run_cmd(cmd: list[str], *, label: str = "cmd", check: bool = True,
                timeout: float = COMMAND_TIMEOUT_SECONDS) -> subprocess.CompletedProcess

- It passes `timeout` to `subprocess.run`, which kills the child when the time runs out.
- On `subprocess.TimeoutExpired` it raises `RuntimeError(f"{label} timed out after {timeout:g}s") from None`,
  even when `check=False`. The message never includes argv, stdout or stderr…

### P17-T01 Bound external commands with a timeout
Files:
- `transcoding/config.py` (edit: add `COMMAND_TIMEOUT_SECONDS = 7200` next to `SEGMENT_DURATION`)
- `transcoding/utils/cmd.py` (edit)
- `transcoding/video/transcription.py` (edit)
Do:
1. In `run_cmd`, add the keyword `timeout: float = COMMAND_TIMEOUT_SECONDS` (imported from `config`).
   Pass it to `subprocess.run`. Catch `subprocess.TimeoutExpired` and raise … Leave every other behavior and print line as is.
2. In `extract_audio`, replace `subprocess.run(cmd, check=True, capture_output=True)` with
   `run_cmd(cmd, label="extract-audio")`, and drop the `subprocess` import.
Test: `transcoding/tests/test_cmd.py` (new)
- `run_cmd([sys.executable, "-c", "import time; time.sleep(5)"], label="sleepy", timeout=0.2)` → …
- `inspect.signature(run_cmd).parameters["timeout"].default` → `config.COMMAND_TIMEOUT_SECONDS == 7200`
```

The rest of the v2 plan worked the same way. It gave nineteen step and branch signatures with their bodies, a checkpoint file table, log strings, patch targets for every test, and a list of the fakes.

## After (v3)

````markdown
# P17 Portable worker

Format: 3
Kind: feature
Approved: pending
Depends on: none
Touches: `transcoding/` (worker only; no server, lockfile, or schema change)

## Goal
Pipeline steps run as plain Python outside Modal, and one local process can run a whole job.
Modal jobs behave exactly as before: same images, same per-step hardware (a GPU only for
encoding and transcription), same retries, same events, same cost.

In: steps and branch logic as Modal-free modules; an in-process runner with tests; job and
model folders from config; a timeout on every external command.
Out: the job spec and attempts (P18); CPU encoding (P19); heartbeats and cancellation (P34);
any caller of the runner (P20); storage settings (P21); any server or protocol change.

## Requirements
C1. Step, branch, and runner modules never import `modal`. Importing them in a fresh interpreter leaves `modal` out of `sys.modules`.
C2. Modal behavior is unchanged: the same functions, images, hardware, retries, schedules,
    claim request, callback bodies, and event replay. Existing Modal tests keep their assertions.
C3. Each step checkpoints in the job folder; a retry resumes from it, so packaging and
    transcription run at most once per job.
C4. Checkpoints store paths relative to the job folder. Absolute paths in checkpoints written
    before this phase still resolve, so in-flight jobs keep working.
C5. `JOBS_DIR` and `MODEL_DIR` are read only in `config.py`. Unset or empty → `/jobs` and
    `/models`. A relative path fails at import, naming the variable.
C6. Every external command has a timeout (default 7200 s, the longest Modal timeout). A timeout
    raises even when exit codes are ignored, and its message never contains argv or output
    (the packager can echo key material).
C7. The local runner retries three units (prepare, video branch, enrichment branch) on Modal's
    retry schedule, and a test derives the delays from the Modal config. Video runs before enrichment.
    A branch that exhausts its retries doesn't stop the other; then the first error is raised
    and the job folder is kept for a resume.
C8. Local failures: a denied claim creates no folder and sends nothing. A preparation failure
    sends `failed`/`preparation_failed` for each requested stage and removes the folder. An
    encode or transcription failure fails only that stage, with no retry.
C9. Logs carry video, job, and worker ids, step labels, and exception type names only.

## Design
Seams that later phases build on (P20's agent calls `run_job`; both runners build a `Job`):

    @dataclass(frozen=True)
    class Job:
        root: Path                   # <JOBS_DIR>/<job uuid>
        payload: dict                # the payload prepare_job receives today
        commit: Callable[[], None]   # Modal: volume commit; local: no-op

    Transcriber = Callable[[Path, float, float], dict]  # (speech.wav, duration s, offset s) → transcript
    def run_job(payload: dict, *, transcriber: Transcriber | None = None,
                sleep: Callable[[float], None] = time.sleep) -> None

Owners: `transcoding/steps.py` holds the step bodies, `transcoding/orchestration.py` the branch logic, and
`transcoding/local_runner.py` the runner. `pipeline.py` keeps only the Modal wrappers. The storage
client moves to `transcoding/utils/storage.py`.

### Choices
| Question | Decision | Why |
| --- | --- | --- |
| Transcription seam | A callable, not a class | Modal wraps it with GPU metrics; one function type is enough |
| Local branch order | Video, then enrichment, synchronously | Readiness first; one GPU never runs the encoder and the speech model at once |
| Retry units | Three units, no per-step retries | Avoids nested retries; checkpoints make a branch retry resume |
| Command timeout | One default, not an env var | Equals the longest Modal timeout; nobody needs to tune it yet |
| Caller of `run_job` | Tests only | P20's agent is the real caller; build nothing ahead |

## Context
Read: D016 (steps are plain Python; Modal wraps each on matching hardware); I09, I10 (packaging and encryption must not change).
Reuse: `transcoding/tests/test_pipeline.py` drives Modal functions in-process and is the regression net for C2;
`run_cmd` in `transcoding/utils/cmd.py` is the only subprocess runner.

## Tasks
- [ ] P17-T01 Bound external commands with a timeout
  Done when: C6 holds for every external command, including the audio extraction that bypasses
  `run_cmd` today; tests cover a timeout, `check=False`, and a child that writes a secret to stderr.
- [ ] P17-T02 Read job and model folders from config
  Done when: C5 holds; Modal images set both variables to their mount points, and no mount
  depends on a developer's environment.
- [ ] P17-T03 Move publication steps into steps.py
  Done when: video and caption publication run from `steps.py` through a `Job`; C2 holds for them;
  a test proves the Modal image includes every local module `pipeline.py` imports.
  Checkpoint: first use of `Job` and the step shape the next tasks copy.
- [ ] P17-T04 Move preparation, encoding and transcription into steps.py
  Done when: C3 and C4 hold for these steps; the claim moves with preparation unchanged; GPU
  metrics stay in the Modal wrapper.
- [ ] P17-T05 Move branch logic into orchestration.py
  Done when: coordinators, cleanup, and expiry call orchestration; existing coordinator tests
  pass with only their patch targets changed.
- [ ] P17-T06 Add the in-process local runner
  Done when: `run_job` meets C1, C7, and C8 with one shared set of fakes, including a resume after
  a failed upload and a branch that exhausts its retries.

## Acceptance
Auto:
- The transcoding test and typecheck commands in AGENTS.md → pass
Manual:
- Serve the Modal app and upload a short video with speech, captions on → it reaches `ready`
  with captions and chapters. Needs Modal credentials and a public tunnel.
- In the Modal dashboard for that run → only encoding and transcription hold a GPU.
````

## What moved to the builder

- **The `run_cmd` signature, the error text, and `from None`.** C6 states the property that matters (no output in the message), and the builder picks the mechanism.
- **Helper names and plumbing:** the absolute-path helper, the mount constant names, and where the image env layer goes.
- **All nineteen step and branch signatures, with their bodies.** Only `Job`, `Transcriber`, and `run_job` cross a seam.
- **Checkpoint file names, progress and log strings, and the checkpoint table.**
- **Test inputs, patch targets, fake setup, and per-task file lists and Do steps.**

## What stayed with the planner

- Compatibility (C2, C4), the security of timeout messages (C6), retry and failure semantics (C7, C8), and the import boundary (C1).
- The two seams later phases depend on.
- Choices that change behavior or cost.
- The task order, and the checkpoint after the first use of the new shape.
