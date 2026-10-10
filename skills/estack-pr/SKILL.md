---
name: estack-pr
description: Prepare an Elixir/Phoenix change for review or publication with accurate verification evidence. Use when summarizing a diff, preparing a commit or PR, or checking release readiness.
---

# Prepare a reviewable change

Inspect the current branch, working tree, intended base, and task authorization. Preserve unrelated user changes. Read repository instructions and use `estack-review` on the relevant diff.

## Verify

Run the project's available gate and any focused checks needed for changed behavior. Record exact commands, results, and limitations. Never claim a browser check, deployment, or passing test that was not performed. Distinguish static validation from runtime behavior.

Inspect migrations, public API changes, job-argument compatibility, dependencies, secrets, and generated files. Confirm documentation matches actual behavior. Resolve concrete failures or state why they remain blocked.

## Summarize

Write a concise description covering:

- Problem and why it matters.
- Behavior changed and meaningful implementation decisions.
- Tests/checks run and their results.
- Migration, rollout, compatibility, or unresolved limitations.
- Relevant issue/source references without including sensitive input.

Use the repository's changelog conventions when requested or required. Do not manufacture screenshots for a server-only change.

## Publish within authority

Use the user's requested workflow. Create a branch/PR when that is authorized or the repository default; commit/push directly only when authorized and permitted. Existing explicit authorization to push to main does not need another confirmation. Do not bypass branch protections, force-push shared history, or trigger production actions outside scope.

After publication, verify the resulting commit/ref and inspect required CI checks. Report the actual outcome and link to the commit or PR. Opening a PR is not evidence of deployment.
