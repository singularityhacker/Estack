---
name: estack-deploy
description: Prepare Phoenix releases, migrations, health checks, and observable rollouts. Use when editing runtime config, deployment pipelines, Docker builds, production topology, or release diagnostics.
---

# Deploy and operate Phoenix

Inspect the existing release process, hosting platform, Elixir/OTP pins, Repo, and deployment topology. Apply the task's authorization separately to code preparation and production execution. Preserve working infrastructure unless a change is requested.

## Runtime configuration

Read deployment-provided secrets/URLs in `config/runtime.exs` when they must be resolved at boot. Compile-time configuration is evaluated when the release is built. Fail clearly for required settings, while allowing disabled integrations and ordinary tests to run without their credentials.

Use the generated project's endpoint server switch consistently (`PHX_SERVER` or explicit `server: true`); an environment variable does nothing unless config reads it. Do not require unrelated vendor credentials for release migration/eval commands.

## Releases and builds

Use the project's generated release/Docker templates and pinned toolchain instead of copying an arbitrary image tag. Ensure configuration needed by dependency compilation is copied before compiling dependencies. Compile assets using the existing build, then assemble the release with required runtime libraries, certificates, locale, and an appropriate non-root user.

Mix is not normally included in a release. Use a release migration module and a deliberate migration job. See the complete [release helper](assets/release.ex.example), adapting `:my_app` and the module name to the application. It supports repositories configured under `:ecto_repos`.

Run `bin/my_app eval "MyApp.Release.migrate()"` in the authorized deployment environment. Use separate backup/recovery and rollback plans; running a down migration can destroy data and is not a universal rollback strategy.

## Rollout compatibility

Use expand/backfill/contract migrations so old and new application versions can overlap. Consider table locks, concurrent index support, feature rollout order, and when old workers stop. Maintain compatibility with persisted job args and API payloads. Do not remove an old schema field while the previous release still needs it.

Set termination grace from request/job durations and platform behavior; coordinate the platform timeout with application/worker shutdown. Monitor reconnect behavior. There is no universal 60-second value suitable for every service.

## Health and resources

Separate liveness (process can run) from readiness (instance can serve traffic). Keep checks bounded and avoid restarting all nodes because of a shared transient database outage.

Size BEAM schedulers, container CPU/memory, and database connections with load and telemetry. Erlang can account for CPU quotas; verify the actual runtime's detected quotas and online schedulers. Monitor throttling, scheduler utilization, run queues, and tail latency instead of categorically removing CPU limits.

For Oban, validate peer/engine choice, pruning, queue budgets, and deploy overlap. A per-node singleton is not a cluster singleton; database pools should fit the database's total connection budget across all replicas.

## Observability

Use stable event names and structured metadata supported by the logging formatter. Carry a correlation/operation ID across HTTP, context, jobs, and vendor calls. Redact credentials, sensitive payloads, and unnecessary identifiers.

Track request errors/latency, database checkout/query time, job failures/retries/age, and critical business outcomes. Attach telemetry handlers once under an intentional lifecycle; handlers execute in the emitting process, must be fast, and detach if they fail. Avoid duplicate attachment on child restarts.

After deployment, verify health and the affected behavior against the intended release SHA. Keep code verification and deployed verification distinct in the report.

## References

- [Phoenix releases](https://hexdocs.pm/phoenix/releases.html)
- [Erlang runtime flags](https://www.erlang.org/doc/apps/erts/erl_cmd.html)
- [Telemetry](https://hexdocs.pm/telemetry/telemetry.html)
