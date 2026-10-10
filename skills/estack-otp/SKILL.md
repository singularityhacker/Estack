---
name: estack-otp
description: Choose and operate Elixir processes, supervision, tasks, and ETS. Use when adding GenServers, concurrent work, process state, fault isolation, or diagnosing mailboxes and timeouts.
---

# OTP patterns

Inspect the supervision tree and installed Elixir/OTP versions. Start with the runtime requirement, not a preference for process-shaped code.

## Choose the mechanism

| Requirement | Starting point |
|---|---|
| Pure transformation | Plain function/module |
| Bounded concurrent work | Task or Task.Supervisor with explicit result/error handling |
| Shared state with serialized operations | GenServer; Agent for very simple state |
| Explicit state/event transitions | Consider `:gen_statem` when complexity warrants it |
| Many reads of shared in-memory data | ETS with an explicit owner and lifecycle |
| Per-entity processes | DynamicSupervisor and Registry |
| Work surviving process/node loss | Durable queue or persisted workflow |

Stateless work can still need concurrency. Supervision and state are separate decisions. Do not choose `spawn_link` solely because a decision tree has no better branch.

## Bound concurrency and failure

Use linked tasks when their failure should fail the caller. Use supervised unlinked tasks when failures must be handled separately. `async_nolink` alone does not make `Task.await` safe: await exits on task failure or timeout.

This illustrative function handles an isolated task's result, failure, and timeout in an ordinary caller:

```elixir
defmodule Estack.Examples.IsolatedTask do
  def run(supervisor, fun, timeout) do
    task = Task.Supervisor.async_nolink(supervisor, fun)

    case Task.yield(task, timeout) || Task.shutdown(task, :brutal_kill) do
      {:ok, result} -> {:ok, result}
      {:exit, reason} -> {:error, {:task_exit, reason}}
      nil -> {:error, :timeout}
    end
  end
end
```

Killing work does not reverse effects already performed. Use a durable idempotent job for important writes.

In GenServers/LiveViews, avoid blocking the mailbox waiting for long work. Handle task result and `:DOWN` messages, clear references, and clean up monitors; use LiveView async APIs where appropriate. Bound async-stream concurrency and handle exits/timeouts. Choose linked versus unlinked stream behavior intentionally.

## Supervision

Use `:one_for_one` for independent children, `:rest_for_one` for ordered dependencies, and `:one_for_all` only when the children must restart together. Set restart intensity based on recovery behavior. A supervisor restarts a process according to its child spec; it does not persist state, retry every Task automatically, or guarantee business completion.

Keep `init` fast. `handle_continue` defers work beyond init but still blocks that process's mailbox while it runs.

## State and access

A GenServer serializes callbacks. Measure mailbox growth and latency before assuming it scales. Use `call` when a reply is required, but recognize that timeouts are not admission control and do not cancel server work automatically. Bound work intake explicitly when needed.

For ETS, document the owner, access mode, restart behavior, and table availability. A protected table lets callers read directly and routes writes through its owner; reads during owner restart may need handling. Use `:persistent_term` only for rarely changed data; updates have system-wide costs.

Name dynamic processes with Registry/via tuples instead of runtime-generated atoms. Use PartitionSupervisor only after measuring a supervisor bottleneck.

## Polling and distribution

Consolidate polling when multiple views need the same external data. Add timeout, backoff, jitter, and bounded work. A named GenServer is a singleton per node, not per cluster. Use an explicit cluster coordination strategy or a durable scheduler if duplicate polling would be harmful.

Keep external I/O out of a busy shared server's callback when it would delay unrelated messages. Broadcast only the data authorized subscribers should receive.

## Diagnose before tuning

Inspect queue length, process memory, reductions, and scheduler utilization over time. There is no universal mailbox length that proves a bottleneck. Use `:sys.get_state` and tracing selectively; state/traces may contain sensitive data. Turn tracing off when finished.

Carry needed locale, request metadata, and identifiers into new processes explicitly. Avoid copying large closures/sockets; reference-counted binaries have different copying behavior from ordinary terms.

## References

- [Task failure and OTP behavior](https://hexdocs.pm/elixir/Task.html)
- [Supervision](https://hexdocs.pm/elixir/Supervisor.html)
