---
name: quality-wall
description: The quality gate for Elixir/Phoenix projects. One alias that runs every check. Use when you need to understand or run the gate, or when a check fails.
---

# The Quality Wall

The wall is one ordered alias that CI runs. A lint, a type error, and a failing test are the same kind of failure.

## The alias

```elixir
# mix.exs
defp aliases do
  [
    verify: [
      "clawbank.check_toolchain",     # Elixir/OTP version matches .tool-versions
      "format --check-formatted",      # Code is formatted
      "deps.unlock --check-unused",    # No unused dependencies
      "compile --warnings-as-errors",  # Zero warnings
      "coveralls.json --raise",        # Coverage above floor
      "dialyzer",                      # Type checking
      "credo --strict",                # Strict linting
      "sobelow --config --skip --exit High",  # Security findings
      "deps.audit",                    # Dependency advisories
      "excellent_migrations.check_safety",    # Migration safety
      "clawbank.quality_report"        # Artifact (not a gate)
    ],
    precommit: [
      "format",                        # Fix formatting first
      "deps.unlock --unused",          # Remove unused deps
      # ... then the same checks as verify
    ]
  ]
end
```

Adapt this to your project. The key principle: **one alias, every check, CI runs it.**

## Rules

1. **Fix the finding the alias printed.** Run the alias again.
2. **Do not add a `credo:disable`, a Dialyzer ignore, a coverage skip, or an audit ignore** without a comment that names the reason.
3. **Do not edit the alias, the workflow, or the hook** to make a red check pass.
4. **Run the single test file while developing.** Run `mix verify` once before you stop.

## Credo strict

```elixir
# .credo.exs
%Credo.Check.Refactor.CyclomaticComplexity{}  # Default cap: 9
%Credo.Check.Refactor.ABCSize{max_size: 50}
%Credo.Check.Refactor.Nesting{}
%Credo.Check.Readability.Specs{}               # @spec on every public function
%Credo.Check.Readability.ModuleDoc{}            # @moduledoc on every module
```

When complexity fails, split the function. Pull a branch into a named helper. Do not add your file to an exclusion list.

## The discarded-error check

A custom Credo check that fails on:

```elixir
_ = Repo.insert(changeset)     # BUG: error is thrown away
_ = Ecto.Multi.new()           # BUG: multi result ignored
_ = Oban.insert(changeset)     # BUG: job insertion unchecked
_ = Phoenix.PubSub.broadcast() # BUG: broadcast failure hidden
```

Match the result with `case`, `with`, or `{:ok, _} =`. The check catches the four call families where a discarded error silently breaks the user's request.

## Dialyzer

- Runs on application code (not just types).
- Ignore file is `dialyzer.ignore-warnings`. Each line has a comment saying why.
- Fix the spec or the code. Do not ignore a module under `lib/<app>/`.

## Sobelow

- Runs at `High` exit level. Low-noise findings fail CI.
- A `sobelow_skip` comment is allowed only next to a constant path, not user input.
- Do not pass `--exit low` or delete the alias.

## Dependency audit

- `deps.audit` fails the build.
- Each ignored advisory ID has a comment naming the GHSA, the exposure, and the condition that re-enables the check.
- Do not pass `--ignore` with no IDs.

## Migration safety

- `excellent_migrations.check_safety` is in the gate.
- Dangerous changes (DROP COLUMN, type change) require a file-level safety comment:

```elixir
# excellent_migrations:safety-assured-for-this-file column_removed
```

- Do not widen `skip_checks` to make a migration pass. Name the exception.

## Toolchain pin

- `.tool-versions` is the single source of truth for Elixir and OTP versions.
- CI reads it. The check task reads it. Do not bump Elixir in one environment.
- Formatter, warnings, and Dialyzer all change across versions.

## Coverage

- Set a minimum floor (e.g., 65%) with `floor_coverage: true`.
- Critical paths (payment matching, order reconciliation) get higher per-file thresholds.
- Do not add your module to `skip_files` to go green.

## Formatting

- `.formatter.exs` imports Ecto, Phoenix, and the LiveView HTML formatter.
- Covers `config`, `lib`, `test`, `priv/*/seeds.exs`, and migration directories.
- Let `mix format` rewrite your files. Do not hand-align pipelines.
- Line length is 120.
