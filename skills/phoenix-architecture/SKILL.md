---
name: phoenix-architecture
description: Phoenix context architecture, domain vs web boundary, module organization, and the API adapter layer. Use when setting up a new feature, deciding where code goes, or structuring contexts.
---

# Phoenix Architecture

## The boundary rule

Business logic lives in `lib/<app>/`. HTTP, LiveView, and MCP live in `lib/<app>_web/`. If the project uses the Boundary library, this is enforced at compile time. A LiveView can call a context. A context cannot reach into the web layer.

```elixir
# lib/my_app.ex
use Boundary, deps: [], exports: :all

# lib/my_app_web.ex
use Boundary, deps: [MyApp], exports: [Endpoint]
```

**Rule:** Put business rules, schemas, and Oban workers in `lib/<app>/<context>/`. Put controllers, LiveViews, and plugs in `lib/<app>_web/`. Call contexts from the web layer. Do not alias `<App>Web` from `lib/<app>/`.

## Context structure

A context is a directory of focused modules, not one giant file.

```
lib/my_app/
  orders/
    order.ex          # Schema
    orders.ex         # Context (public API)
    fulfillment.ex    # Operations
    sync_job.ex       # Oban worker
```

- Name schemas for the noun (`Order`, `Report`).
- Name operations for the job they do (`Fulfillment`, `Documents`).
- Name workers with a `Job` suffix.
- Keep the public API on the context module (`Orders`). List public functions in `@moduledoc`.
- Everything else is `defp` or in a submodule callers do not alias.

## The API adapter layer

When the same business operation is a LiveView action, a REST endpoint, and an MCP tool, add a thin adapter in `lib/<app>/api/<area>.ex`:

```elixir
defmodule MyApp.Api.Orders do
  def call(tool, args, user) when is_map(args) do
    case Map.get(dispatch_table(), tool) do
      nil -> {:error, "unknown_tool"}
      fun when is_function(fun, 2) -> fun.(user, args)
    end
  end
end
```

The adapter owns tool names, JSON envelopes, and the dispatch table. It calls the context. It does not talk to the database.

## Web entrypoints

Use `use MyAppWeb, :live_view` (or `:controller`, `:html`). Do not hand-roll `use Phoenix.LiveView` -- it misses verified routes and layout helpers.

## Routing

- The router is `use Phoenix.Router, helpers: false`.
- Link and redirect with `~p` sigils: `~p"/orders/#{order}"`.
- Do not call generated `Routes.*_path` helpers.

## Naming conventions

| Thing | Convention | Example |
|---|---|---|
| LiveView | `*Live` suffix, file matches | `OrdersLive` in `orders_live.ex` |
| Multi-screen feature | `feature_live/` directory | `orders_live/index.ex`, `orders_live/show.ex` |
| Context module | Plural noun | `MyApp.Orders` |
| Schema module | Singular noun | `MyApp.Orders.Order` |
| Oban worker | `*Job` suffix | `MyApp.Orders.SyncJob` |

## Public IDs

Rows that agents and URLs see use a generated `public_id` (e.g., `ord-abc123`). Integer primary keys stay inside the database. Do not put the integer PK in a URL or API response.

## Docs

- `docs/README.md` is the index of current design records.
- `docs/archive/` is old research. Do not read it unless a current doc points you there.
- When the doc and the code disagree, trust the code.

## HTTP client

Use `Req` for outbound HTTP. Do not add `:httpoison`, `:tesla`, or `:httpc`. Share one Finch pool with bounded idle time.
