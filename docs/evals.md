# Evaluating Estack

`estack-eval` compares the code agents produce when given the same task with different skill instructions. It supports **no skills versus Estack** and **previous skills versus a proposed revision**. Package tests still verify that the pack installs; these evaluations check behavior produced by agents.

The first pilot is published in [the pilot report](../evals/results/2026-10-11-pilot/README.md). Both conditions passed 18/18 behavioral checks across three tasks, and the blind reviewer called all three pairs ties. This demonstrates a working initial evaluation path, not an established improvement from Estack.

## Start in your coding agent

```text
Use estack-eval to compare this skill revision with the previous version.
Use the same tasks and settings, keep workers blind, run the executable
checks, and ask a separate reviewer to score anonymous outputs.
```

The [skill](../skills/estack-eval/SKILL.md) supplies the workflow. The [protocol](../skills/estack-eval/references/protocol.md) defines fairness, isolation, failure handling, and reporting. The runner is portable and bundled with the skill; public development cases require this repository checkout. No new model subscription or API integration is needed by the runner. Your host must actually support fresh independent agents to execute the comparison.

## Initial cases

| Case | Behavior checked | What it does not prove |
|---|---|---|
| [Tenant boundary](../evals/cases/tenant-boundary/task.md) | Tenant-scoped access, owner/viewer permissions, protected ownership fields, input validation | Actual Ecto SQL queries, database races, or Phoenix transport wiring |
| [Task isolation](../evals/cases/task-isolation/task.md) | Successful values, task crashes, timeouts, child cleanup, mailbox behavior | Distributed recovery, durable work, or every scheduler race |
| [Webhook receipt](../evals/cases/webhook-receipt/task.md) | Exact-byte verification, persistence-before-ack, duplicates, retriable storage errors | A real Plug signature verifier, transactional database, or Oban adapter |

These are small executable domain-boundary tasks with no Hex dependencies. They are public development/calibration cases. They are too small and explicit to establish general agent effectiveness; they may be easy for a strong baseline.

## Run from a checkout

Requirements: Python 3.10+; Elixir 1.18+ and OTP compatible with it for grading; POSIX for process cleanup. CI pins Elixir 1.18.4 / OTP 27.3. Python performs orchestration; Elixir evaluates the resulting application behavior.

```bash
python3 skills/estack-eval/scripts/eval.py validate --suite evals/cases
python3 -m unittest discover -s tests/evals -p 'test_*.py'

python3 skills/estack-eval/scripts/eval.py prepare \
  --case evals/cases/task-isolation \
  --baseline none --candidate skills \
  --out evals/runs/my-comparison --workspace-root /tmp/workrooms --repeats 3
```

Calibrate the graders before starting workers. The runtime suite verifies that every reference solution passes and every seeded bug fails a critical check. It also tests the complete prepare/record/grade/judge/report path without calling a model.

The prepare command prints only opaque worker IDs and paths. Keep its control directory, manifest, rubric, reference solutions, and condition mapping away from workers. Launch a fresh agent for each project with the same request and budget. Do not inherit the coordinator conversation. Read the generated `REQUEST.md` and project instructions; do not attach the evaluation protocol to a worker.

For version comparisons, point `--baseline` at the old checkout's `skills` directory and `--candidate` at the new one. Select skill names in `case.json`; compare compatible names or create normalized snapshots first. Do not mix other code or tooling changes into the treatment.

Record each worker, including failures:

```bash
python3 skills/estack-eval/scripts/eval.py record \
  --run evals/runs/my-comparison --worker ledger-example --status completed
python3 skills/estack-eval/scripts/eval.py grade \
  --run evals/runs/my-comparison --allow-execution
python3 skills/estack-eval/scripts/eval.py judge \
  --run evals/runs/my-comparison --out /tmp/review-packet
```

Replace `ledger-example` with the printed ID. Optional metadata flags record observed model/effort/time/tokens/cost; unknown values remain null. They do not configure agents. The runner never treats a worker's claim that it read a skill as proof.

Read submitted code before running it. Separate directories and timeout/output limits are **not a security sandbox**. Use a disposable, secrets-free environment; use containers/VMs and restricted mounts/network for stronger isolation. The current host-assisted pilot uses protocol-level blinding on a shared host, not an enforced access boundary.

Launch one fresh reviewer with only `/tmp/review-packet`. Have it follow `REVIEW.md` and fill `judgment.json`. Both variants are presented as A/B, with code, rubric, and executable check results. Critical failures cannot be overridden by prose scoring. Then reveal the mapping:

```bash
python3 skills/estack-eval/scripts/eval.py report \
  --run evals/runs/my-comparison --judgment /tmp/review-packet/judgment.json
```

The run contains frozen source, check results, logs, mappings, and Markdown/JSON reports. Do not publish private application data or raw transcripts accidentally; `evals/runs/` is ignored by Git. Curate publishable evidence under `evals/results/`.

## Gates and limitations

- Every planned worker remains visible, including errors, timeouts, and invalid artifacts. Retrying creates a new run; do not overwrite unfavorable evidence.
- Protected fixture/instruction changes, symlinks, missing check IDs, contradictory exit status, and invalid rubric entries fail validation.
- Grades, label mappings, and accepted judgments cannot be overwritten through the runner. The first valid judgment is locked before the report reveals conditions. A driver-only calibration repair must be explicitly recorded before scoring; old grader snapshots are retained. Task/rubric changes require a new experiment.
- Missing or unsupported grading runtimes stop the coordinator without assigning worker scores. An interrupted grading attempt is preserved and cannot be resumed over partial artifacts; retain it and prepare a new run.
- Reviewers use a 0–2 scale per criterion with evidence. Objective correctness, subjective judgments, and unobserved cost/time stay separate.
- Provider-neutral orchestration currently uses your host manually; there are no verified Cursor/Claude/Codex headless adapters, secret handling, or billing integrations.
- The runner does not independently attest model identity, skill reads, OS isolation, transcript integrity, or resistance to malicious code that tries to forge grading behavior.
- There is no significance test or overall benchmark score. Three tasks and many assertions are still three tasks.

## Next work

Add harder tasks from real regressions, including Ecto authorization/transaction tests against a database, LiveView event boundaries, and Oban retries/idempotency. Reserve held-out tasks before tuning instructions. Repeat paired runs within each model/settings group, capture actual tool traces and costs where available, and report confidence intervals only when the sample/design supports them. Keep ties and regressions public alongside wins.
