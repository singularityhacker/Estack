---
name: estack-doctor
description: Inspect an Elixir/Phoenix project's setup without modifying it. Use for readiness checks, installed dependency/tool detection, initial Estack adoption, or a prioritized engineering report.
---

# Estack doctor

Produce a read-only readiness report. Read repository instructions first. Run the bundled static inspector when Python 3.10+ is available, resolving the script relative to this skill directory:

```bash
python3 scripts/doctor.py --project /path/to/project --format json
```

The inspector reads a bounded set of project/config files. It does not evaluate Elixir, run Mix, install packages, contact services, or read `.env` files. Treat its output as hints: Mix configuration can be dynamic, and a dependency in `mix.lock` is not proof it is enabled at runtime.

## Review the evidence

1. Confirm the project root and umbrella children. Read `mix.exs`, `mix.lock`, existing instructions, and relevant test/config files.
2. Identify versions and uncertainty, the auth scope/user interface, Ecto adapter or Ash use, background jobs, and UI conventions.
3. Inspect gate aliases and actual configuration. Dependency presence alone does not mean a check runs in CI.
4. Identify only actionable gaps: unsafe input ownership, missing authorization tests, unusable checks, absent vendor isolation, or unclear rollout behavior.
5. Use `estack-security`, `estack-quality`, or another relevant skill for a focused follow-up. Avoid auditing unrelated files indefinitely.

## Report

Return a concise summary, then findings with priority, evidence/file location, recommended fix, and verification method. Separate confirmed defects, project choices, and unknowns. Do not invent a numeric readiness score.

If a runtime/client is unavailable, say what remains unverified. Do not edit files or run migrations as part of the doctor unless the user separately authorized fixes. Point to `estack-setup` for adoption and `estack-feature`/`estack-debug` for implementation.
