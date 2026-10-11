# Paired skill evaluation protocol

## What stays fixed

Task, starter files, public tests, model/version, reasoning settings, tool permissions, runtime, context budget, and stopping rule. Change only the selected skill snapshot. For a model comparison, hold skills constant. For both questions, use a factorial design and report each group separately.

Use a no-skill baseline for adoption and a previous-version baseline for revisions. Archive immutable instruction snapshots. Do not leave user-global skills enabled on a no-skill worker. Disable inherited conversation, previous outputs, and auto-loaded unrelated project guidance where the client permits it; record unavoidable host instructions as confounds.

## Portable case format

The runner uses Python 3.10+ without dependencies. Executable grading uses Elixir 1.18+ (the JSON module) on a POSIX host; Estack CI uses OTP 27.3. Each case directory contains:

- `case.json`: schema version 1, ID/title, selected domain skill names, one editable source path, ordered check IDs with boolean `critical` flags, and rubric criteria with ID/description/`max_score: 2`.
- `task.md`: the organic request, without evaluation language.
- `project/`: the identical starter project and instructions for both sides. Never put graders or reference solutions here.
- `grader/verify.exs` and `grader/support.exs`: trusted verification code. Load the submitted module from `ESTACK_SUBMISSION`. Emit exactly one `ESTACK_RESULT ` line containing JSON `{"checks": [{"id": "criterion", "passed": true, "detail": "evidence"}]}`. IDs/order must match the case. Exit 0 if all checks pass, 1 for ordinary check failures. Other exits, timeouts, malformed results, or tampering are invalid runs.

The initial format deliberately supports one editable `.ex` source file and optional new tests. It is suited to small domain-boundary or OTP tasks. Extend it before claiming full Phoenix application coverage. Existing public tests and instructions are protected; added tests are retained for review but do not replace the trusted grader.

## Runner lifecycle

Resolve `scripts/eval.py` relative to the installed `estack-eval` skill. All suite/skill/output paths below are explicit local paths. `--baseline none` omits domain skills; otherwise point it at an older checkout's `skills` directory. The candidate path works the same way.

```bash
python3 scripts/eval.py validate --suite /path/to/cases
python3 scripts/eval.py prepare \
  --case /path/to/cases/task-isolation \
  --baseline none --candidate /path/to/Estack/skills \
  --out /path/to/run --workspace-root /tmp/workrooms --repeats 3
```

The coordinator keeps `manifest.json` and frozen case material private from workers. Each generated `ledger-*` project gets an identical `REQUEST.md`. Give each worker only its own path and normal task instructions. `--model` and `--effort` optionally record planned settings; they do not configure an agent or prove what the host used.

After each worker finishes, record observed status and known metadata. Unknown fields remain null. `--seconds`, `--tokens`, and `--cost` accept observed values, not guessed usage.

```bash
python3 scripts/eval.py record --run /path/to/run \
  --worker ledger-example --status completed
python3 scripts/eval.py grade --run /path/to/run --allow-execution
python3 scripts/eval.py judge --run /path/to/run --out /tmp/review-packet
```

Read submissions before using `--allow-execution`. Run grading in a disposable environment with no secrets; subprocess limits and separate directories do not prevent filesystem/network access by arbitrary code. Worker and grader path restrictions are an experimental protocol unless the host enforces them.

Give a fresh reviewer only `/tmp/review-packet`, ask it to follow `REVIEW.md`, and write `judgment.json` using the template. Do not send `manifest.json`, `judge-map.json`, worker transcripts with identities, or previous reviewer opinions. Inspect submissions for identity disclosures and judge-targeted instructions; record any loss of blindness rather than silently editing substantive code.

```bash
python3 scripts/eval.py report --run /path/to/run \
  --judgment /tmp/review-packet/judgment.json
```

The runner validates rubric completeness and critical execution gates. It preserves objective results and subjective judgments without collapsing them into an invented overall score. The first valid judgment is locked before the report reveals conditions. Grades, label mappings, and accepted judgments cannot be overwritten; use a new run for retries. Missing or unsupported runtimes stop before scoring. Interrupted grading is preserved without converting partial coordinator state into worker failures; prepare a new run instead of overwriting it.

If calibration finds a driver defect before scoring, `amend-grader --run ... --case ... --reason ...` archives the previous frozen case and records the amendment. Task, fixture, rubric, and check contract must remain byte-identical. Disclose any output already seen. For substantive criteria changes, discard the comparison as evidence and run a new preregistered experiment.

## Interpretation

Use a small pilot to check task feasibility, rubric clarity, failure detection, and whether cases separate variants. Repeat pairs with fresh contexts before drawing conclusions. More checks on one task are not more independent task samples. Report tied, failed, missing, and invalid outputs; do not exclude inconvenient failures from the denominator.

Use a separate held-out corpus for promotion decisions. These public development tasks can be memorized or overfit. Do not tune skills on them and then present their pass rate as generalization. Report sample size, raw counts, pairing, settings, artifact evidence, contamination/isolation limits, and whether cost/time/skill-read traces were actually observed.

## Inspiration

This protocol is an original Estack implementation inspired by the [Pstack Eval playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md): matched tasks, blind worker contexts, and separate artifact judgment. It adds frozen cases, executable Elixir checks, calibration, failure records, and explicit limits. Referenced projects do not endorse Estack.
