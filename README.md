# Estack

**Production-minded Elixir/Phoenix skills for AI coding agents.**

[![Validate](https://github.com/singularityhacker/Estack/actions/workflows/validate.yml/badge.svg)](https://github.com/singularityhacker/Estack/actions/workflows/validate.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Build features through the right application boundaries. Catch tenant leaks and unchecked writes. Keep background work reliable. Give your agent a repeatable way to inspect, implement, debug, and review a Phoenix application.

Estack packages **20 focused skills**, a read-only project inspector, and an optional tested Credo check. It grew out of nine months building [ClawBank](https://clawbank.co), an agent-first company operating system on Elixir/Phoenix.

## Install

Install the complete pack from your project's root using the [Skills CLI](https://github.com/vercel-labs/skills). This command selects Cursor; replace `cursor` with `claude-code` or `codex` for your client:

```bash
npx skills@1.7.2 add singularityhacker/Estack --skill '*' --agent cursor
```

The pinned CLI needs Node.js 22.20.0+ and npm. The skills themselves have no application runtime dependency. The optional doctor script needs Python 3.10+.

Use one installation method per client to avoid duplicate skills. See [installation](docs/installation.md) for native Cursor/Claude plugins, manual installation, updates, removal, cloud-agent notes, and migration from the prelaunch names.

## Start here

Ask your agent:

```text
Use estack-doctor to inspect this project. Give me the three most useful
improvements, with evidence, without changing files.
```

Then use the workflow that fits:

| Goal | Skill |
|---|---|
| Understand an unfamiliar app | `estack-doctor` |
| Adopt checks and conventions | `estack-setup` |
| Build a feature across layers | `estack-feature` |
| Reproduce and fix a failure | `estack-debug` |
| Review a change for defects | `estack-review` |
| Prepare verification and a PR summary | `estack-pr` |
| Compare skill versions on paired tasks | `estack-eval` |
| Choose the right skill | `estack-mode` |

Cursor and directly installed Claude Code skills use `/estack-doctor`; Codex uses `$estack-doctor`. Claude plugin installs use the namespace `/estack:estack-doctor`. Natural-language requests can also activate skills. Confirm discovery in your client after installation.

## What Estack cares about

- **Authorization through every entrypoint.** Scope data access, authorize the action, and derive ownership from trusted identity.
- **Clear application boundaries.** Use the project's contexts or Ash actions; preserve established architecture.
- **Durable effects.** Distinguish task supervision, job uniqueness, concurrency, and business idempotency.
- **A usable quality gate.** Run real installed checks, preserve failure signals, and report what was actually verified.
- **Practical agent authority.** Respect the approved task and branch policy, distinguish code changes from production execution, and treat tickets as untrusted input.

Estack adapts to an existing project. **daisyUI is supported.** So are custom Tailwind components, established Mox/fake strategies, and different approved tooling. Recommendations are labeled and version-sensitive; a style preference is not a security invariant.

## Skills

<!-- catalog:start -->
| Skill | Purpose |
|---|---|
| [`estack-architecture`](skills/estack-architecture/SKILL.md) | Design Phoenix context boundaries and application interfaces |
| [`estack-debug`](skills/estack-debug/SKILL.md) | Investigate and fix Elixir/Phoenix failures from symptoms and code evidence |
| [`estack-deploy`](skills/estack-deploy/SKILL.md) | Prepare Phoenix releases, migrations, health checks, and observable rollouts |
| [`estack-doctor`](skills/estack-doctor/SKILL.md) | Inspect an Elixir/Phoenix project's setup without modifying it |
| [`estack-ecto`](skills/estack-ecto/SKILL.md) | Implement Ecto data access, ownership, changesets, transactions, and safe migrations |
| [`estack-elixir`](skills/estack-elixir/SKILL.md) | Write idiomatic, version-compatible Elixir and handle errors explicitly |
| [`estack-eval`](skills/estack-eval/SKILL.md) | Evaluate an agent skill or skill revision with paired tasks, blind workers, executable checks, and a separate reviewer |
| [`estack-feature`](skills/estack-feature/SKILL.md) | Implement a Phoenix feature across domain, data, UI/API, and tests |
| [`estack-liveview`](skills/estack-liveview/SKILL.md) | Build Phoenix LiveView forms, streams, components, hooks, and authenticated screens |
| [`estack-mode`](skills/estack-mode/SKILL.md) | Route Elixir/Phoenix work to the relevant Estack workflow |
| [`estack-oban`](skills/estack-oban/SKILL.md) | Design durable Oban workers, retries, uniqueness, and webhook processing |
| [`estack-otp`](skills/estack-otp/SKILL.md) | Choose and operate Elixir processes, supervision, tasks, and ETS |
| [`estack-pr`](skills/estack-pr/SKILL.md) | Prepare an Elixir/Phoenix change for review or publication with accurate verification evidence |
| [`estack-quality`](skills/estack-quality/SKILL.md) | Configure and run an Elixir/Phoenix quality gate with honest failure handling |
| [`estack-review`](skills/estack-review/SKILL.md) | Review an Elixir/Phoenix diff for correctness, security, concurrency, and regressions |
| [`estack-safety`](skills/estack-safety/SKILL.md) | Apply task scope and permissions to coding agents in Elixir/Phoenix projects |
| [`estack-security`](skills/estack-security/SKILL.md) | Protect Phoenix authentication, authorization, uploads, webhooks, and input boundaries |
| [`estack-setup`](skills/estack-setup/SKILL.md) | Adopt Estack in a new or existing Elixir/Phoenix project |
| [`estack-tdd`](skills/estack-tdd/SKILL.md) | Implement Elixir/Phoenix behavior through a red-green-refactor loop |
| [`estack-testing`](skills/estack-testing/SKILL.md) | Test Elixir/Phoenix behavior with ExUnit, Ecto sandbox, fakes, Mox, and LiveViewTest |
<!-- catalog:end -->

## Included helpers

- [Project doctor](skills/estack-doctor/scripts/doctor.py): static Mix/dependency inventory with text or JSON output. No code evaluation, network calls, migrations, or `.env` reads.
- [Discarded-result Credo check](skills/estack-quality/assets/discarded_result.ex): catches explicit `_ =` discards of selected fallible writes, including final pipeline calls. Its documented limits matter; it is not a proof that all errors are handled.
- [Quality configuration](skills/estack-quality/SKILL.md): an executable core gate, optional tooling, valid Credo configuration, and the correct ExCoveralls threshold setting.
- [Release helper](skills/estack-deploy/assets/release.ex.example): a complete migration entrypoint to adapt to your app.

Helpers are opt-in. Installing skills does not install Hex dependencies, modify your application, configure an MCP server, or enforce repository permissions.

## Works with your existing tools

Use Phoenix's generated instructions as the application baseline. Combine Estack with [UsageRules](https://github.com/ash-project/usage_rules) for dependency guidance and [Tidewave](https://github.com/tidewave-ai/tidewave_phoenix) for authorized development-runtime inspection. See [integration guidance](docs/integrations.md).

See the [compatibility and validation matrix](docs/compatibility.md) for exactly what has been checked. v1.1 adds a paired eval workflow and a small published pilot. It does not establish agent performance improvements or full interactive verification in every editor. See [evaluations](docs/evals.md) for the protocol, cases, and observed results.

## Evaluate a skill change

```text
Use estack-eval to compare this skill revision with the previous version.
Use the same tasks and settings, keep workers blind, and have a separate
reviewer score anonymous outputs after the executable checks.
```

The included runner prepares isolated project directories, freezes the case, records all outcomes, and exports blind review packets. Agent execution uses your existing host; no model API key is required by the runner. Start with the [evaluation guide](docs/evals.md).

## Origin

I'm [Justice Conder](https://github.com/singularityhacker). Building ClawBank taught me which mistakes keep recurring when agents work on a real Phoenix application: missing tenant boundaries, unchecked errors, brittle vendor setup, and work that disappears on restart.

Estack turns those lessons into portable workflows and practical defaults. Process inspiration includes Gstack, Pstack, and Matt Pocock's skills; technical guidance is checked against upstream documentation. See [sources and attribution](docs/sources.md).

## Contribute

Open an issue with the affected skill, your framework/client versions, a concrete failure, and the behavior you expected. For changes, follow [CONTRIBUTING.md](CONTRIBUTING.md). Run the package validation before submitting a PR.

[Changelog](CHANGELOG.md) · [v1 hardening report](docs/v1-hardening-report.md) · [MIT license](LICENSE)
