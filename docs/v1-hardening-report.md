# Estack v1 hardening report

Date: 2026-10-10. Scope: improve the preannouncement release and publish directly to `main`, as authorized by the maintainer. Public demonstrations and agent benchmarks are excluded.

## Completed implementation

- [x] Review every original skill and separate invariants from project preferences.
- [x] Remove the daisyUI prohibition and preserve existing UI/test/toolchain conventions.
- [x] Correct authorization, scope contracts, error handling, task lifecycle, and Oban semantics.
- [x] Replace unavailable ClawBank-specific commands/tool assumptions with portable guidance.
- [x] Ship the optional discarded-result Credo check, coverage/Credo configs, and complete release helper.
- [x] Add a read-only doctor script and doctor/feature/PR workflows.
- [x] Namespace the catalog and document migration from prelaunch names.
- [x] Add Claude packaging and document Cursor/Claude/Codex installation, updates, and removal.
- [x] Add Codex display metadata and useful invocation prompts to all 19 skills.
- [x] Add integration guidance for Phoenix instructions, UsageRules, Tidewave, Ash, and umbrellas.
- [x] Rework the README, preserve the ClawBank origin, record provenance, and create a changelog.
- [x] Add package/helper/installer validation and CI.

## Validation record

The following checks passed locally on the release contents:

| Check | Observed result |
|---|---|
| Package gate | All 19 skills, both manifests, UI metadata, router, catalog, and local resource links pass |
| Skill Creator validator | All 19 skill folders pass |
| Python regression suite | 13 tests pass, including read-only inspection, umbrellas, excluded files/symlinks, and package-gate failure cases |
| Elixir helper suite | 7 ExUnit tests pass: selected write detection, handled-result exclusions, configured aliases, source parsing, file errors, and task success/crash/timeout |
| Fixture formatting | `mix format --check-formatted` passes |
| Installer smoke tests | All 6 combinations pass: Cursor, Claude Code, and Codex, each in copy and symlink mode; 19 skills plus resources installed and removed while preserving unrelated content |
| Independent review | All 19 skills and supporting files reviewed; doctor symlink handling and Node minimum findings fixed |
| Optional Credo adoption checks | Guard compiles without Credo; example config parses; configured check reports the expected issue |

Local toolchain: Python 3.12.14, Node.js 24.19.0, Skills CLI 1.7.2, Elixir 1.18.4, OTP 27.3, and Credo 1.7.19. The Mix fixture lockfile records exact dependency resolution. The doctor was also run against the fixture and correctly reported its static dependency inventory.

GitHub Actions now runs package/Python/installer checks and Elixir helper/formatting checks on pushes and pull requests. Consult the [workflow history](https://github.com/singularityhacker/Estack/actions/workflows/validate.yml) for hosted-run status. The [compatibility matrix](compatibility.md) explains the limits of these checks.

## Issues caught during validation

- Replaced reliance on Credo's non-shipped test helper with its shipped source/check APIs.
- Corrected uninstall handling for the shared `.agents/skills` location and documented exact-source versus local-checkout removal.
- Specified the pinned installer's Node.js 22.20.0 minimum.
- Prevented the doctor from following project-internal symlinks into excluded files and handled loops without crashing.
- Added package checks for stale catalogs, missing bundled resources, resources outside an installable skill, and incorrect UI invocation prompts.

## Deferred and limitations

- Public demo, video, full Phoenix reference app, and agent performance benchmarks: deliberately deferred by the maintainer for v1.
- Interactive invocation in every editor/native plugin: requires the actual client environment; do not infer it from copied files.
- Exhaustive framework/database/hosting version matrices: not claimed.
- Five unnamed Elixir packs mentioned in the original README: exact provenance unavailable; the unsupported count was removed rather than inventing attribution.
- Marketplace listing/review: not part of this repository hardening pass.

See [CHANGELOG.md](../CHANGELOG.md) for the full enhancement list and [CONTRIBUTING.md](../CONTRIBUTING.md) for commands to reproduce the checks.
