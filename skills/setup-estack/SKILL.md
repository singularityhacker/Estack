---
name: setup-estack
description: Configure estack for a new or existing Elixir/Phoenix project. Detects project structure and recommends setup. Use for initial setup or reconfiguration.
---

# Setup Estack

## Steps

### 1. Detect the project

Read `mix.exs` and answer:

- What is the app name? (e.g., `:my_app`)
- What is the web module? (e.g., `MyAppWeb`)
- Is Phoenix installed? What version?
- Is Ecto installed? What database?
- Is Oban installed?
- Is the Boundary library installed?
- Is Credo installed? Is there a `.credo.exs`?
- Is Dialyzer configured?
- Is Sobelow installed?
- Is ExCoveralls or another coverage tool configured?
- Is `excellent_migrations` installed?
- Does a `verify` or `precommit` alias exist in `mix.exs`?
- Does an `AGENTS.md` file exist? (Phoenix 1.8+ generates one)

### 2. Show the results

Present a summary:

```
Project: my_app (Phoenix 1.8.2)
Database: PostgreSQL via Ecto
Background jobs: Oban
Boundary: installed
Quality gate: verify alias found
AGENTS.md: exists (Phoenix-generated)
```

### 3. Recommend setup

Based on what's detected, recommend:

**If no quality gate exists:**
- Suggest adding a `verify` alias with the checks from `/quality-wall`
- List which tools need to be added as dependencies

**If no Boundary:**
- Suggest adding `boundary` to enforce context isolation

**If no AGENTS.md:**
- Suggest creating one with the project's conventions

**If AGENTS.md exists but is the Phoenix default:**
- Suggest extending it with estack conventions

### 4. Write configuration (with approval)

Only write files after the user confirms. Offer to:

- Extend or create `AGENTS.md` with estack conventions
- Add the `verify` alias to `mix.exs` (suggest, don't write without approval)
- Create a `.credo.exs` with the recommended checks if none exists
- Add the discarded-error custom Credo check

### 5. Confirm

Tell the user what was written and what skills are now available.

List the skills:
- `/estack-mode` -- Router, picks the right skill
- `/phoenix-architecture` -- Context boundaries, module organization
- `/ecto-patterns` -- Schemas, queries, migrations, transactions
- `/liveview-patterns` -- Auth, forms, streams, hooks, components
- `/oban-patterns` -- Workers, queues, cron, testing
- `/elixir-testing` -- Fixtures, fakes, isolation, property tests
- `/elixir-tdd` -- Red-green loop for Elixir
- `/elixir-review` -- Code review checklist
- `/quality-wall` -- The quality gate
- `/investigate` -- Bug investigation
- `/agent-safety` -- Safety rules and autonomy boundaries
