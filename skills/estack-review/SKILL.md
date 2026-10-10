---
name: estack-review
description: Review an Elixir/Phoenix diff for correctness, security, concurrency, and regressions. Use when reviewing a PR or checking changes before committing or deployment.
---

# Review Elixir/Phoenix changes

Read the diff, project instructions, affected callers, and tests. Review code even when CI is failing; report the failure alongside other findings. Do not modify code during a review unless fixes were requested.

## Prioritize defects

- **Authorization:** scoped reads/writes, action permissions, server-stamped ownership, and cross-tenant tests. Opaque IDs are not access control.
- **Integrity:** database constraints, rollback, concurrent updates, idempotent external effects, and checked enqueue results.
- **Architecture:** existing context/Ash interfaces, consistent Scope/User contracts, and actual boundary enforcement.
- **LiveView:** both mounts, event authorization, correct forms/slots, stream IDs, scoped PubSub, and appropriate async versus durable work.
- **OTP:** linked/unlinked failure behavior, timeouts, cleanup, mailbox blocking, restart semantics, and node versus cluster scope.
- **Oban:** return values supported by the locked version, retry budget, duplicate execution, durable intake, and old job args.
- **Migrations/releases:** lock impact, rollout compatibility, runtime configuration, and safe deployment ordering.
- **Tests:** meaningful assertions, negative cases, sandbox ownership, controlled vendors, and targeted browser coverage where needed.
- **Quality:** the existing gate, accurate tool configuration, no unjustified suppressions, and honest verification results.
- **Agent operations:** authorized scope, instruction injection, protected-path policy, least-privilege tools, and guidance versus enforcement.

Use the relevant domain skills for depth. Do not flag a style preference (Mox, daisyUI, line length, module names) as a defect when it follows project conventions.

## Output actionable findings

For each finding, include severity, file/line location, the condition that triggers the problem, its consequence, and a concrete remedy. Distinguish confirmed defects from questions that need evidence. Avoid speculative piles of low-confidence concerns.

State what was reviewed and which checks ran. If no actionable issues were found, say so and name any important coverage limits. A passing gate does not prove domain correctness.
