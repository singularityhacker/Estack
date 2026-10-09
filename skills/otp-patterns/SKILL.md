---
name: otp-patterns
description: OTP process architecture for Elixir apps. When to use GenServer, Task, Agent, or plain functions. Supervision strategies, ETS patterns, and process pitfalls. Use when making process design decisions or debugging concurrency.
---

# OTP Patterns

## The Iron Law: No Process Without a Runtime Reason

Before creating a GenServer, Agent, or process, answer YES to at least one:

1. Do I need mutable state that persists across calls?
2. Do I need concurrent execution?
3. Do I need fault isolation?

All three NO = use plain functions and modules. Modules organize code. Processes are for runtime.

**Common rationalizations that are wrong:**
- "I need a process to organize this code" -- modules organize code
- "GenServer is the Elixir way" -- plain functions are also the Elixir way
- "I'll need state eventually" -- YAGNI
- "It's just a simple wrapper process" -- simple wrappers become bottlenecks

## The Decision Tree

```
Need state?
  No -> Plain function
  Yes -> Complex behavior?
    No -> Agent (trivial state only)
    Yes -> Supervision needed?
      No -> spawn_link
      Yes -> Request/response?
        No -> Task.Supervisor
        Yes -> Explicit state machine?
          No -> GenServer
          Yes -> :gen_statem
```

## GenServer Is a Bottleneck by Design

A GenServer processes ONE message at a time. Before creating one, ask:

1. Do I need serialized access?
2. Will this become a throughput bottleneck?
3. Can reads bypass via ETS?

### The ETS Read Bypass

GenServer owns the ETS table. Writes serialize through the GenServer. Reads bypass it entirely:

```elixir
def init(_) do
  table = :ets.new(__MODULE__, [:named_table, :set, :protected, read_concurrency: true])
  {:ok, %{table: table}}
end

# Write goes through GenServer (serialized)
def handle_call({:put, key, value}, _from, state) do
  :ets.insert(state.table, {key, value})
  {:reply, :ok, state}
end

# Read bypasses GenServer entirely (concurrent)
def get(key) do
  case :ets.lookup(__MODULE__, key) do
    [{^key, value}] -> {:ok, value}
    [] -> :error
  end
end
```

## GenServer Rules

- **Fast `init/1`**: defer expensive work with `{:ok, state, {:continue, :load_data}}`. `handle_continue/2` runs before any messages.
- **Public API module**: callers use `MyApp.Cache.get/1`, never raw `GenServer.call/2`.
- **`@impl true`** on every callback.
- **`call` for backpressure**: use `call/3` when you need a reply or ordering. `cast/2` only for true fire-and-forget.
- **Set timeouts**: `GenServer.call(pid, msg, 5_000)`. The default is 5s, but be explicit.
- **Reply with `{:error, reason}`** for expected failures. Let unexpected failures crash for supervisor restart.

## Task.Supervisor, Not Task.async

`Task.async` links -- if the task crashes, the caller crashes too.

```elixir
# Production: supervised, fault-isolated
Task.Supervisor.async_nolink(MyApp.TaskSupervisor, fn -> do_work() end)

# Quick scripts only: linked, crashes propagate
Task.async(fn -> do_work() end)
```

- Always have a corresponding `Task.await/2` or `Task.yield/2` with bounded timeout.
- Handle `Task.async_stream` exits: match both `{:ok, result}` and `{:exit, reason}`. Use `on_timeout: :kill_task`.

## DynamicSupervisor + Registry

For per-user, per-session, or per-entity processes:

```elixir
# Never create atoms dynamically for process names
# BAD: String.to_atom("worker_#{user_id}")
# GOOD:
{:via, Registry, {MyApp.Registry, "worker:#{user_id}"}}
```

Use `PartitionSupervisor` to scale DynamicSupervisor for high throughput.

## Supervision Strategies Encode Dependencies

| Strategy | Meaning | Use when |
|---|---|---|
| `:one_for_one` | Independent children | Default. Children don't depend on each other. |
| `:one_for_all` | Interdependent | All must restart together. Rare. |
| `:rest_for_one` | Sequential dependency | Later children depend on earlier ones. |

Set `:max_restarts` and `:max_seconds` to prevent restart loops. Think about failure cascades BEFORE coding.

## Storage Options

| Need | Use |
|---|---|
| Memory cache, many readers | ETS with `:read_concurrency` |
| Static config, rarely changes | `:persistent_term` (faster reads than ETS) |
| Disk persistence | DETS (2GB limit) |
| Transactions/distribution | Mnesia |

## Debugging OTP Processes

```elixir
:sys.get_state(pid)        # Current state of any OTP process
:sys.trace(pid, true)      # Trace all events (TURN OFF when done)
Process.info(pid, :message_queue_len)  # Queue > 100 = bottleneck
```

## Process Pitfalls

- **Messages are copied between processes** (except binaries >64 bytes). Extract minimal data before spawning.
- **Process dictionary is unidiomatic** -- pass state explicitly.
- **Atom table is finite and never GC'd** -- never create atoms from runtime data.
- **Gettext locale is process-local** -- capture before spawning, pass explicitly.
- **Reference-based selective receive** -- `make_ref()` + `receive do {^ref, result} ->` to avoid O(n) mailbox scan.

## External Polling Architecture

Never have every LiveView poll an external API. Use a single GenServer:

```elixir
defmodule MyApp.PricePoller do
  use GenServer

  def init(_) do
    schedule_poll()
    {:ok, %{price: nil}}
  end

  def handle_info(:poll, state) do
    price = fetch_price()
    Phoenix.PubSub.broadcast(MyApp.PubSub, "prices", {:price_updated, price})
    schedule_poll()
    {:noreply, %{state | price: price}}
  end

  defp schedule_poll, do: Process.send_after(self(), :poll, :timer.seconds(30))
end
```

LiveViews subscribe to PubSub. One process polls, all clients receive.

## Telemetry

Phoenix, Ecto, and most libraries emit telemetry events. Attach handlers in `Application.start/2` (never in GenServer init -- handlers detach permanently if they raise):

```elixir
:telemetry.attach("slow-queries", [:my_app, :repo, :query], &handle_query/4, %{})
```

Use `:telemetry.span/3` for timing operations. Use structured logging: `Logger.info("event", key: value)`.
