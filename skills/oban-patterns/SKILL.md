---
name: oban-patterns
description: Oban worker, queue, cron, and job patterns for Phoenix apps. Use when adding background jobs, scheduling work, or debugging Oban issues.
---

# Oban Patterns

## Every worker declares queue, attempts, and uniqueness

```elixir
use Oban.Worker,
  queue: :builder,
  max_attempts: 2,
  unique: [
    period: 600,
    fields: [:args],
    keys: [:company_id, :doc_key],
    states: [:available, :scheduled, :executing, :retryable]
  ]
```

**Rules:**
- Set `queue:` -- the default queue hides which feature is stuck.
- Set `max_attempts:` -- unbounded retries on a broken job burn resources.
- Use `unique:` when the same business key must have one in-flight job.
- Return `{:ok, _}` or `{:discard, reason}` for permanent failures.
- Match on `{:ok, _}` / `{:error, _}` from `Oban.insert`. Do not write `_ = Oban.insert(...)`.

## Cron lives in config

```elixir
# config/config.exs
config :my_app, Oban,
  repo: MyApp.Repo,
  plugins: [
    {Oban.Plugins.Cron, crontab: [
      {"0 */6 * * *", MyApp.Orders.SyncJob},
      {"*/5 * * * *", MyApp.Heartbeat.PingJob}
    ]}
  ],
  queues: [default: 10, builder: 5, mailer: 5]
```

Add schedules as crontab entries. Do not insert a cron row from a LiveView.

## Peer is :global for single-node

On platforms like Render, the Postgres lease can survive a deploy and the new node never becomes leader. A single-node app does not need a database lease:

```elixir
peer: Oban.Peers.Global
```

Switch to `Oban.Peers.Postgres` only when running multiple nodes.

## Testing is :manual

```elixir
# config/test.exs
config :my_app, Oban, testing: :manual
```

Assert on the job args. Drain in the test that owns the worker:

```elixir
assert_enqueued worker: SyncJob, args: %{order_id: order.id}
Oban.drain_queue(queue: :builder)
```

Do not turn testing back to `:inline` globally. A cron plugin that fires during tests inserts jobs into a sandbox that is about to roll back.

## Task.Supervisor for ephemeral work

Short fan-out (PDF download, inbound webhook processing) uses a named `Task.Supervisor` in the application children:

```elixir
# lib/my_app/application.ex
children = [
  {Task.Supervisor, name: MyApp.WebhookSupervisor}
]
```

```elixir
Task.Supervisor.start_child(MyApp.WebhookSupervisor, fn ->
  process_webhook(payload)
end)
```

`Task.start` is unlinked and vanishes on deploy. A supervisor makes the crash visible. Anything the user waits on belongs in Oban.

## PubSub

One named server. Do not create a second PubSub:

```elixir
Phoenix.PubSub.broadcast(MyApp.PubSub, "orders:#{order.id}", {:order_updated, order})
```

Subscribe from `mount` only when `connected?(socket)`. Handle `{:error, _}` from `broadcast`.
