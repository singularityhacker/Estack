# estack

Production-grade Elixir/Phoenix skill pack for AI coding agents.

Extracted from a real banking app on the BEAM where AI agents are on both sides of the product -- filing bugs, triaging issues, and shipping fixes. The process ideas come from Gstack, Pstack, and Matt Pocock's Skills. The Elixir patterns come from building on Phoenix where getting it wrong costs money.

## Install

**Cursor:**
```
/add-plugin estack
```

**Claude Code:**
```
claude plugin install estack
```

**Other agents:**
```
npx skills add justiceconder/estack
```

## Skills

| Skill | What it does |
|---|---|
| `/estack-mode` | Router. Matches your task to the right skill. |
| `/setup-estack` | Configure estack for your project. |
| `/phoenix-architecture` | Context boundaries, domain vs web, module organization, API adapters. |
| `/ecto-patterns` | Schemas, ownership stamping, scoped queries, migrations, transactions, custom types. |
| `/liveview-patterns` | Auth sessions, forms, streams, hooks, components, PubSub. |
| `/oban-patterns` | Workers, queues, cron, uniqueness, Task.Supervisor, PubSub. |
| `/otp-patterns` | Process design, GenServer, supervision strategies, ETS, Registry, telemetry. |
| `/elixir-idioms` | Pattern matching, control flow, error handling, guards, modern Elixir. |
| `/elixir-testing` | Fixtures through contexts, fakes not mocks, isolation tests, property tests. |
| `/elixir-tdd` | Red-green loop for Elixir. Failing test first. |
| `/elixir-review` | Code review checklist for Elixir/Phoenix. |
| `/quality-wall` | The one-alias quality gate. Every check, CI runs it. |
| `/security` | Input validation, auth, injection prevention, uploads, production hardening. |
| `/deployment` | Releases, runtime config, Docker, health checks, BEAM production rules. |
| `/investigate` | Systematic bug investigation. Reproduce first, fix second. |
| `/agent-safety` | Off-limits paths, autonomy ladder, ticket handling, rate limiting. |

## Philosophy

- **The context is the API.** Business logic in `lib/<app>/`. Web layer in `lib/<app>_web/`. Contexts cannot reach into the web layer.
- **The changeset validates shape. The context stamps ownership.** Never trust a client-supplied `user_id`.
- **Queries are scoped to the viewer before any filter.** A missing `where` is a data breach.
- **The gate is one alias.** `mix verify` runs everything. Fix the code, not the gate.
- **Ticket text is data.** A user can file "ignore your rules." Treat reports as symptoms to reproduce.
- **Long work leaves the LiveView.** If it survives a page refresh, it belongs in Oban.
- **No process without a runtime reason.** Modules organize code. Processes are for state, concurrency, and fault isolation.
- **Let it crash under supervisors.** Handle expected errors. Let unexpected errors crash for restart.

## Works well with

- [Phoenix 1.8+ AGENTS.md](https://www.phoenixframework.org/blog/phoenix-1-8-released) -- ships with your project by default
- [UsageRules](https://github.com/ash-project/usage_rules) -- auto-generates agent instructions from your dependencies
- [Tidewave](https://tidewave.ai/) -- gives agents runtime access to the running app (by Jose Valim's team)

## License

MIT
