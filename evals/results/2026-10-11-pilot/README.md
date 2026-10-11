# First Estack evaluation pilot

Date: 2026-10-11. **Result: three ties.** Both conditions passed 18/18 behavioral checks. The blinded reviewer gave each output 6/6 rubric points and no preference in any pair. These observations do not establish an effectiveness improvement from Estack.

## Question and setup

Does supplying the relevant Estack domain skills change the quality of a small Elixir implementation task? We compared no domain skills with the selected skills from commit `296cc44e828e8cf0c14a8a0842309064fc488495`.

There were three tasks, one pair per task, six workers total. Every worker started with a fresh context (`fork_turns=none`), an identical project/request within its pair, and an opaque `ledger-*` workspace. The variant mapping stayed with the coordinator. Workers were instructed to remain in their project and not inspect other projects. A seventh fresh agent reviewed anonymous A/B outputs, seeing the task, rubric, code, and executable check results together.

All workers and the reviewer inherited the same host configuration. Exact model identifiers and reasoning settings were not exposed; those fields are null, along with unobserved timings, token counts, and costs. There was one implementation attempt per worker and no outcome-driven retries. No explicit per-worker token/time ceiling was configured. This is a pilot of the evaluation machinery, not a controlled comparison across model families.

## Results

| Task | Without skills | With Estack | Blind rubric scores | Preference |
|---|---|---|---|---|
| Tenant boundary | 6/6 checks | 6/6 checks | A 6/6; B 6/6 | Tie |
| Task isolation | 6/6 checks | 6/6 checks | A 6/6; B 6/6 | Tie |
| Webhook receipt | 6/6 checks | 6/6 checks | A 6/6; B 6/6 | Tie |

All six submissions passed their critical gates and protected-file checks. The coordinator read every implementation and its added tests before executing source, then agreed with the reviewer that these tasks did not distinguish the conditions. The OTP implementations were identical; the other differences did not change required behavior.

The seeded starter implementations failed relevant critical checks during calibration. Independent reference implementations pass the runtime calibration suite. This shows that the graders detect the supplied defects; it does not establish that they detect every plausible defect.

## Evidence

Each task directory includes the exact frozen case and rubric, instruction hashes, initial file hashes, submitted code/tests, verification logs, objective grades, locked blind judgment, revealed mapping, and JSON/Markdown report. The recorded original workspace paths are provenance, not portable execution locations.

- [Tenant report](tenant-boundary/report.md), [machine-readable evidence](tenant-boundary/report.json), and [blind judgment](tenant-boundary/accepted-judgment.json).
- [Task isolation report](task-isolation/report.md), [machine-readable evidence](task-isolation/report.json), and [blind judgment](task-isolation/accepted-judgment.json).
- [Webhook report](webhook-receipt/report.md), [machine-readable evidence](webhook-receipt/report.json), and [blind judgment](webhook-receipt/accepted-judgment.json).
- [Pilot metadata](pilot.json) and [reviewer instructions](judge-instructions.md).

To replay a submitted artifact, set `ESTACK_SUBMISSION` to the absolute path of its `.ex` file under the task's `artifacts/` directory, then run `elixir` on that task's frozen `case/grader/verify.exs`. This replays executable checks, not the original model generation. The artifact directory names map to conditions in `report.json`; the blind A/B mapping is preserved separately.

## Calibration repair and later strengthening

Before scoring any outputs, calibration found that the original OTP driver used an unsupported guard form in `refute_receive`. It was replaced with the intended two-tuple mailbox pattern. The task, rubric, public project, and check IDs were unchanged. Worker completion summaries had already arrived; they were not used to alter the acceptance criteria. The previous case and explicit amendment remain under [the archived case](task-isolation/amendments/1/case/case.json) and [manifest](task-isolation/manifest.json).

Independent harness review subsequently demonstrated a different implementation that stopped timed-out work but left a monitor message behind. The initial grader checked mailbox cleanup only after success, so that mutant passed. The current development case is revision 2 and adds timeout/crash mailbox checks, with a regression test for the leaking implementation. This published pilot retains its original six-check OTP contract and has not been retroactively rescored.

Review also led to locked judgments after unblinding, rejection of incomplete grading without worker scores, and runtime preflight before scoring. These defects concern the harness; they were repaired and regression-tested before publication.

## Limits and next experiment

- Three small tasks, one paired run per task. Eighteen assertions are not eighteen independent task samples.
- The prompts state the expected contracts clearly. A strong baseline can solve them without additional instructions.
- These are domain-boundary exercises, not full Phoenix/Ecto/Oban integrations.
- Workers and reviewer share a host configuration. A different-family reviewer was not established.
- Separate directories and instructions provided protocol-level blinding; the host did not enforce private mounts or prohibit filesystem access to other workspaces.
- Worker tool transcripts were not independently archived. Skill presence and requested loading are recorded; actual skill use is not attested.
- Public tasks can be memorized or overfit; these are development cases, not a held-out benchmark.

The next experiment should use harder real regression tasks, repeated pairs, verified model/settings/tool traces, and a separately reserved held-out corpus. Preserve this tie result while expanding coverage. Do not interpret it as evidence that Estack has no value, or as evidence that it improves performance.
