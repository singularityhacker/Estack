---
name: estack-oban
description: Design durable Oban workers, retries, uniqueness, and webhook processing. Use when enqueueing jobs, configuring queues or cron, testing workers, or handling external side effects.
---

# Oban patterns

Inspect the locked Oban version, engine, Repo, plugins, and deployment topology. Use supported options and preserve the project's conventions.

## Worker contracts

Declare an intentional queue and retry budget. Oban already has a bounded default attempt count; tune attempts and backoff to the failure mode. Configure a timeout where unbounded execution is inappropriate.

Return `:ok` or `{:ok, value}` only on success. Return `{:error, reason}` for retryable failures. Use the installed version's terminal cancellation result for permanent failures (modern Oban uses `{:cancel, reason}`; `{:discard, reason}` is deprecated). Never mark a failed operation successful merely to stop retries.

Job args are serialized data, generally string-keyed when delivered to `perform`. Pass stable IDs and fetch current data with appropriate scoping. Avoid putting secrets or unnecessary PII in persisted args.

## Idempotency before uniqueness

Assume a job may run more than once. Separate three concerns:

1. **Insertion deduplication:** `unique` can suppress matching enqueues within a configured window.
2. **Concurrency control:** queue/engine limits or explicit locks control simultaneous execution.
3. **Business idempotency:** a repeated execution must not repeat an irreversible effect.

Include `:worker` and the relevant argument keys in a uniqueness policy unless cross-worker exclusion is deliberate. Understand the engine's guarantees; uniqueness is not a universal exactly-once guarantee.

Use database uniqueness/conditional state transitions and provider idempotency keys for important effects. Handle a crash after the provider accepts an operation but before local completion is recorded; reconcile using the stable operation ID.

## Transactions and enqueueing

Match enqueue errors. Insert the domain write and job in the same transaction when they share a Repo/database. Use the Oban Multi integration supported by the installed version. Never assume a job in another database rolls back with the domain transaction.

Treat conflicting unique inserts as a domain decision: `{:ok, job}` can represent a conflict; inspect `job.conflict?` when that distinction matters.

## Webhook intake

Verify signature and replay requirements against the raw request body using the provider's specification. Persist/deduplicate receipt and enqueue durable work before acknowledging delivery when losing the event would matter. Handle persistence failure deliberately so delivery can be retried.

Use Task.Supervisor only for ephemeral work that may safely disappear on deploy or node failure. Supervised tasks are still in memory. Do not use fire-and-forget webhook processing for a business-critical event.

## Scheduling and topology

Keep static schedules in the existing Cron configuration; use supported dynamic scheduling features only when needed. Configure pruning with retention appropriate to auditing and support.

Keep the default peer unless there is a demonstrated reason to change it. `Oban.Peers.Global` requires understanding Erlang distribution and rollout overlap; two disconnected nodes can each elect a leader. Do not prescribe it as a universal single-node hosting fix.

Size database pools from measured checkout time, query duration, concurrency, and the database connection budget. Job concurrency is not a formula for one permanently held connection per job.

## Testing

Prefer `testing: :manual` for enqueue assertions and explicit worker execution. Preserve existing deliberate alternatives. Use `Oban.Testing` helpers and ensure spawned work has SQL sandbox access.

Test transient failures, terminal failures, duplicate delivery, and transaction rollback. Confirm job completion after effects, not just insertion. Test backward compatibility of args when old jobs may execute new worker code after a deploy.

## References

- [Worker return values and configuration](https://hexdocs.pm/oban/Oban.Worker.html)
- [Uniqueness guarantees](https://hexdocs.pm/oban/unique_jobs.html)
- [Oban testing](https://hexdocs.pm/oban/testing.html)
