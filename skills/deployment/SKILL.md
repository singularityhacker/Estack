---
name: deployment
description: Deployment, release, and production patterns for Elixir/Phoenix apps. Runtime config, Docker, health checks, and operational concerns. Use when deploying or configuring production.
---

# Deployment

## Config: Runtime vs Compile-Time

**Secrets and URLs go in `config/runtime.exs`.** Compile-time config (`config.exs`, `prod.exs`) is baked into the release and cannot read env vars at boot.

```elixir
# config/runtime.exs
config :my_app, MyAppWeb.Endpoint,
  url: [host: System.fetch_env!("PHX_HOST")],
  http: [port: String.to_integer(System.get_env("PORT", "4000"))],
  secret_key_base: System.fetch_env!("SECRET_KEY_BASE"),
  server: true  # Required for releases
```

**Use `System.fetch_env!/1` (with bang) for required secrets** so the release crashes on startup if missing.

## Releases

- **`mix` is not available in production releases.** Run migrations via release commands:

```elixir
# lib/my_app/release.ex
defmodule MyApp.Release do
  def migrate do
    load_app()
    for repo <- repos() do
      {:ok, _, _} = Ecto.Migrator.with_repo(repo, &Ecto.Migrator.run(&1, :up, all: true))
    end
  end

  def rollback(repo, version) do
    load_app()
    {:ok, _, _} = Ecto.Migrator.with_repo(repo, &Ecto.Migrator.run(&1, :down, to: version))
  end

  defp load_app do
    Application.load(:my_app)
  end
end
```

- **Run `mix assets.deploy` before `mix release`** in Docker builds. Phoenix 1.8+ does not need Node.js.
- **Set `PHX_HOST` and `PHX_SERVER=true`** in runtime config. Without these, URL generation breaks and the server won't start.

## Docker

Multi-stage build:

```dockerfile
# Build stage
FROM hexpm/elixir:1.18.4-erlang-28.0.2-debian-bookworm AS builder
RUN apt-get update && apt-get install -y build-essential git
WORKDIR /app
ENV MIX_ENV=prod
COPY mix.exs mix.lock ./
RUN mix deps.get --only $MIX_ENV && mix deps.compile
COPY config config
COPY lib lib
COPY priv priv
COPY assets assets
RUN mix assets.deploy && mix compile && mix release

# Runtime stage
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y libstdc++6 openssl libncurses5 locales \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/_build/prod/rel/my_app ./
CMD ["bin/my_app", "start"]
```

## Health Checks

Split liveness and readiness:

```elixir
# Liveness: app is running (no DB check)
get "/health/liveness", HealthController, :liveness

# Readiness: app can serve traffic (includes DB)
get "/health/readiness", HealthController, :readiness
```

Liveness returns 200 without querying the database. Only readiness checks the DB. Collapsing both means a DB blip either gets masked or takes healthy instances out of rotation.

## BEAM-Specific Production Rules

- **No CPU limits for BEAM.** The scheduler assumes it owns all cores. CPU limits cause scheduler collapse with latency spikes.
- **Graceful shutdown >= 60 seconds.** Shorter kills in-flight requests and WebSocket connections.
- **One toolchain pin** (`.tool-versions`) for laptop, CI, and production. Formatter, warnings, and Dialyzer all change across versions.

## Oban in Production

- **Peer is `:global` for single-node.** On platforms like Render, the Postgres lease can survive a deploy.
- **Pruner plugin** to keep the jobs table from growing: `{Oban.Plugins.Pruner, max_age: 7 * 24 * 60 * 60}`.
- **Pool size rule:** `pool_size >= num_queues + sum(queue_limits) + buffer`.

## Structured Logging

```elixir
# Good
Logger.info("order_created", order_id: order.id, user_id: user.id)

# Bad
Logger.info("Created order #{order.id} for user #{user.id}")
```

Structured logging enables filtering and aggregation. Attach telemetry handlers in `Application.start/2` for Phoenix/Ecto events.

## Environment Configuration

- **Fresh app should boot without third-party credentials.** Use Fakes in dev/test.
- **`.env.example` committed with placeholders.** `.env` files in `.gitignore`.
- **Guard optional service credentials:** only require S3/Redis creds when the integration is enabled, not on every boot. Release `eval` commands fail otherwise.
