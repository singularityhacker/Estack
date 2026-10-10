---
name: estack-architecture
description: Design Phoenix context boundaries and application interfaces. Use when adding a feature, deciding where modules belong, introducing API/MCP adapters, or working in an Ash or umbrella application.
---

# Phoenix architecture

Read project instructions, neighboring modules, and `mix.lock`. Preserve the existing context layout; Phoenix generators commonly place a context at `lib/my_app/orders.ex` and schemas under `lib/my_app/orders/`.

## Put behavior behind a public interface

Keep business rules, schemas, and durable job orchestration in the domain application. Keep HTTP, LiveView, serialization, and transport authentication at the web boundary. Call public context functions from web code; avoid reaching into context internals or querying Repo directly from an event handler.

Use modules to organize code. Add a GenServer only when a runtime requirement justifies one.

If Boundary is already installed, check its configuration and exported interfaces before changing dependencies. Propose it for a project that needs enforced boundaries; do not add it to every app automatically. Exporting everything from the top-level application does not enforce isolation between individual contexts.

## Use the project's authorization contract

For Phoenix scope-based apps, pass the existing scope struct into context functions. For older apps, preserve their authenticated-user or policy interface. Do not mechanically replace `%User{}` with `%Scope{}` without adapting callers and tests.

Stamp ownership server-side and authorize the operation inside the public boundary so REST, LiveView, and jobs do not accidentally enforce different policies.

## Adapt multiple transports

Let each transport decode input and encode responses around the same business operation. Introduce a shared application-service adapter only when it removes real duplication. Keep transport-specific tool names and JSON envelopes out of the domain unless the project intentionally models them there.

Use an explicit dispatch allowlist. Never derive module/function atoms from untrusted tool names. Classify tools by actual read/write/admin capability and enforce permissions on the server.

## Existing ecosystems

- **Ash:** inspect domains, resources, actions, policies, and `ash_*` UsageRules. Use the established actions rather than introducing a parallel context/Repo implementation that bypasses policies.
- **Umbrellas:** inspect `apps/*/mix.exs`, application dependencies, and the shared configuration. Do not assume one web app or Repo.
- **API-only/library apps:** skip LiveView, Tailwind, database, or background-job setup when absent.

## Web conventions

Use the project's `MyAppWeb` macros so components inherit imports, layouts, and verified routes. Prefer `~p` where Phoenix.VerifiedRoutes is configured; do not rewrite legacy routes as unrelated cleanup.

Keep naming consistent with neighboring code: plural contexts, singular schemas, and established LiveView/worker names. Reuse Req/Finch if present; preserve an existing HTTP adapter until a migration is requested.

## Public identifiers

Use the project's UUID, opaque identifier, or integer convention. Opaque IDs can reduce enumeration, but do not provide authorization. Verify access regardless of identifier format. Changing public IDs requires API and migration planning.

## Design records

Record meaningful boundary decisions and exceptions in the repository's existing documentation. If docs and code disagree, investigate whether the code is defective or the docs stale; do not automatically treat the implementation as the intended contract.
