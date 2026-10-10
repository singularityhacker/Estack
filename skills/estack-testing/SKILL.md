---
name: estack-testing
description: Test Elixir/Phoenix behavior with ExUnit, Ecto sandbox, fakes, Mox, and LiveViewTest. Use when adding tests, isolating vendor calls, testing concurrent processes, or choosing browser coverage.
---

# Elixir testing

Read existing test support and configuration. Preserve working test conventions. Ordinary tests must not need live vendor credentials, real funds, or uncontrolled external services. Use the database adapter the project supports; PostgreSQL is not mandatory for every Elixir app.

## Test observable behavior

Test public context functions or Ash actions for domain behavior, plus focused tests for complex pure functions and changesets when useful. Build ordinary fixtures through valid application interfaces. Direct Repo fixtures can be appropriate for constraints, legacy states, or efficient setup; make the reason explicit and preserve invariants.

For every scoped operation, exercise another tenant/user and relevant roles. Test reads, writes, deletes, preloads, aggregates, and unauthorized events. Use `:not_found` when resource existence is private and explicit denial where the product intentionally distinguishes it.

## Vendor boundaries

Use behaviours and deterministic fakes for repeatable development/test flows when that fits the app. Preserve Mox where used; use expectations when interaction behavior matters. Prefer existing Req.Test or Bypass infrastructure for HTTP request/response assertions. Do not impose a mocking migration on an unrelated feature.

Keep fake behavior aligned with the boundary contract, including errors, timeouts, and malformed responses. Configure implementations before application startup. Do not mutate global Application env from an async test.

## SQL sandbox and concurrent processes

Use the project's DataCase/ConnCase and sandbox setup. Enable async only when the database adapter and shared state permit it. Spawned processes need explicit sandbox ownership/allowance or the established caller-tracking mechanism; arrange this before queries run.

Use `start_supervised!` for test-owned processes. Avoid global names when concurrent tests could collide. Synchronize with messages, monitors, or observable state rather than `Process.sleep`. Use bounded `assert_receive` timeouts and clean up tasks before sandbox checkout ends.

Bypass and property tests are not inherently synchronous: global configuration, process ownership, and database use determine whether async is safe.

## LiveView and browser behavior

Prefer LiveViewTest for server-side events, form validation, authorization, redirects, and streams. Select meaningful stable DOM IDs and assert behavior rather than large raw HTML snapshots.

Use focused browser tests/manual verification for JavaScript hooks, actual uploads, focus, navigation, and external browser integrations that the server test cannot execute. Keep that suite small and run it when the changed behavior requires it; do not ban browsers or require them for every server change.

## Jobs and properties

Use Oban manual mode when asserting enqueueing; perform/drain jobs deliberately in worker tests. Exercise error results, retries, idempotency, and transactional rollback.

Use property tests for meaningful invariants: unauthorized transitions are rejected, totals are conserved, normalization is idempotent. Derive expectations from the domain specification, not the same implementation function being tested. Use state-machine sequences where ordering is the behavior under test.

## Verification and coverage

Run the smallest relevant test first, then related tests and the project gate. Document any missing services/toolchain instead of claiming success. Use coverage to find untested behavior, not as a substitute for useful assertions.

For ExCoveralls, `minimum_coverage` sets the threshold; `floor_coverage` controls rounding. Keep approved exclusions narrow and documented. Use the installed coverage tool's actual capabilities rather than assuming per-file thresholds exist.

## References

- [Ecto SQL sandbox](https://hexdocs.pm/ecto_sql/Ecto.Adapters.SQL.Sandbox.html)
- [LiveViewTest](https://hexdocs.pm/phoenix_live_view/Phoenix.LiveViewTest.html)
- [Mox ownership](https://hexdocs.pm/mox/Mox.html)
