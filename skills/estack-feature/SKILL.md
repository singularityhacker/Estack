---
name: estack-feature
description: Implement a Phoenix feature across domain, data, UI/API, and tests. Use when a request changes behavior across application layers and needs a coherent implementation workflow.
---

# Build a feature

Read repository instructions and the authorized request. Inspect existing code and locked dependency versions. Reuse the project's architecture, scope/user contract, database, UI library, and test conventions.

## Work through the change

1. State the observable acceptance criteria and affected actors. Resolve only missing decisions that materially affect implementation.
2. Trace the existing public context or Ash action. Identify ownership, tenant boundary, action permissions, and failure contracts.
3. Plan the smallest coherent change through persistence, domain, and UI/API. Decide whether background work needs durability, retries, and idempotency.
4. Add meaningful tests around the changed behavior, including unauthorized/other-tenant and failure cases. Use `estack-tdd` where a test-first loop is useful.
5. Implement with the relevant skills: `estack-architecture`, `estack-ecto`, `estack-liveview`, `estack-oban`, and `estack-security`. Load only what the change needs.
6. If a migration is required, design rollout compatibility. Preparing a migration is distinct from executing it against production.
7. Run targeted checks, then the existing project gate. Use browser verification for browser-only behavior when applicable. Inspect the final diff.
8. Summarize behavior, verification, and remaining limitations. Use `estack-pr` if preparing a commit/PR is in scope.

Do not convert the project to Estack's preferred tooling as incidental work. Honor existing authorization without repeated confirmation. Keep unrelated refactors separate.
