---
name: estack-setup
description: Adopt Estack in a new or existing Elixir/Phoenix project. Use for initial configuration, quality-gate setup, dependency guidance, and integration with existing agent instructions.
---

# Set up Estack

## Inspect first

Read the repository's instructions and use `estack-doctor` if installed. Identify actual versions from `mix.lock` and the toolchain, application/umbrella structure, auth contract, database, Ash, job system, test tooling, styling, and existing check aliases.

Do not assume the project needs Phoenix, Postgres, Oban, Boundary, or daisyUI if absent. Preserve working choices such as Mox, alternate databases, or custom UI components. Read dependency UsageRules and version-matched docs where needed.

## Make a scoped adoption plan

Report existing capabilities, missing prerequisites, and a short ordered list of changes. Distinguish required correctness from optional conventions. Reuse `precommit`/`verify` or other existing gates; do not overwrite them.

If setup changes are already authorized, implement them. If the user requested only an assessment, produce a proposed diff/plan before requesting permission to apply it. Do not ask again for every file within an approved setup.

## Configure incrementally

- Extend the existing agent instruction file without replacing generated or dependency-managed sections.
- Use `estack-quality` for tested check assets and a reference gate. Start with installed tools and add dependencies only when selected for the project.
- Keep fast checks and full checks distinguishable. Establish a realistic coverage baseline using the coverage tool's actual threshold setting.
- Add boundary enforcement only where it solves an architectural problem; configure actual context exports if context isolation is intended.
- Detect Tidewave/UsageRules and document how to use them. Do not silently start an MCP server or connect it to production.
- Use deterministic development/test integrations so a fresh checkout does not need vendor secrets for ordinary work.

## Verify and report

Run the changed configuration and the available project gate. Confirm skill discovery in the user's client when accessible; otherwise give the exact check to perform and label it unverified. List changed files, new dependencies, commands run, and any deferred decisions.

Refer to `estack-mode` for the full skill catalog rather than maintaining a second incomplete list here.
