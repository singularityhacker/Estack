# Changelog

## 1.1.0 — 2026-10-11

### Added

- `estack-eval`, bringing the pack to 20 skills, with an installable comparison runner and evaluation protocol inspired by Pstack.
- Paired skill/no-skill and version-to-version project preparation, opaque worker directories, frozen cases/instruction hashes, and explicit failure/timeout records.
- Elixir behavioral graders for tenant authorization, task failure isolation, and durable webhook acknowledgement.
- Protected-file checks, bounded grading, anonymous A/B reviewer packets, rubric validation, and critical gates that a judge cannot override.
- Known-good and seeded-bug calibration, harness regression tests, and CI without model API credentials.
- An auditable first pilot: six workers, three paired tasks, 18/18 checks per condition, and three blinded ties. No efficacy improvement is claimed.

### Notes

- Python remains orchestration glue; Elixir performs behavioral verification. The runner does not launch models or provide a hostile-code sandbox.
- The pilot records its grader syntax amendment, shared-host limits, unknown model/cost details, and next steps toward harder held-out tasks.

## 1.0.0 — 2026-10-10

### Added

- `estack-doctor`, `estack-feature`, and `estack-pr` workflows; 19 skills in the complete pack.
- Read-only static Mix project inspector with JSON/text output, umbrella/dependency hints, bounded reads, and no `.env`/network/code evaluation.
- Doctor symlink exclusions and regression coverage for excluded files, linked directories, and loops.
- Optional `Estack.Check.DiscardedResult` Credo implementation, documented detection limits, configuration, and regression tests.
- Complete release migration helper; corrected coverage and Credo configuration examples.
- Claude Code plugin manifest alongside the existing Cursor manifest.
- Codex UI metadata and explicit invocation prompts for every skill.
- Client installation/update/removal instructions, native plugin routes, cloud-worker notes, and a prelaunch name migration table.
- Generated README skill catalog, package validation, isolated installer smoke tests, helper tests, and GitHub Actions CI.
- Compatibility evidence, integration guidance, source attribution, contribution guide, and this changelog.

### Changed

- Namespaced all skills with `estack-` to reduce collisions. See the installation guide for every old/new name.
- Reworked the README around outcomes, installation, first use, workflows, and explicit limits.
- Made framework rules version-aware and preserved existing architecture, UI, mocking, formatter, and toolchain choices.
- Explicitly supported daisyUI and targeted browser verification.
- Generalized ClawBank-specific maintenance tools and separated interactive task authorization from unattended policies.
- Deepened tenant/action authorization, idempotency, durable webhook handling, sandbox ownership, rollout compatibility, and observability guidance.

### Fixed

- Canonical repository/homepage metadata and documented Cursor local-plugin path.
- Scope/User contract inconsistencies and client-controlled ownership examples.
- Incorrect implication that scoped queries alone authorize every action.
- Misleading coverage-floor configuration, invalid Credo configuration shape, and absent project-specific quality tasks.
- Incomplete file-resource and release-helper examples; invalid form actions-slot assumption.
- Task failure/timeout semantics, stateless-concurrency decision guidance, and supervision/durability distinctions.
- Overbroad CPU-limit, shutdown-time, database-pool, Oban-peer, and browser-testing rules.
- Oban success-versus-permanent-failure guidance and uniqueness-versus-concurrency distinctions.
- Removed unsupported claims about unnamed source packs and blanket replacement of established libraries.

### Scope

- Deferred public demonstrations and agent benchmarks for this v1 release.
- Documented the difference between installer/helper validation and interactive editor or full application validation.

## 0.1.0 — 2026-10-09

- Initial public pack of 16 Cursor-oriented Elixir/Phoenix skills.
