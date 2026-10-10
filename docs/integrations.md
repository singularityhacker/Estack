# Integrations and project policy

## Existing instructions

Read applicable repository instructions before changing code. User authorization and client-enforced policy take precedence over Estack defaults. Preserve security/integrity invariants; treat formatting, naming, UI libraries, and testing libraries as project choices.

When a rule conflicts with code, inspect intent and tests rather than assuming either is correct. Record deliberate exceptions in the repository's established documentation. Don't overwrite Phoenix-generated or dependency-managed instruction sections.

## Phoenix, daisyUI, and older projects

Phoenix 1.8-style examples commonly use auth scopes and new generated components. Older apps may use a user struct, different layouts, or Tailwind v3. Follow the installed versions and generated code. Support daisyUI themes/components where present and custom UI where chosen.

## UsageRules

If installed, use the project's existing UsageRules configuration and dependency rules. Inspect `mix help usage_rules.sync` and the locked version before changing generated output. It can supply dependency-specific instructions and skill resources; Estack supplies the cross-cutting workflow.

Avoid duplicate or contradictory always-loaded instructions. Keep Estack names distinct from generated dependency skills. Review generated diffs and preserve hand-written sections according to the package's supported mechanism.

## Tidewave

Tidewave's Phoenix MCP can expose runtime evaluation and other development tools. If it is already configured, use it to confirm behavior and investigate failures. First verify the environment, capabilities, and authorization. Evaluation may read or mutate the app/database; it is not inherently read-only.

Keep runtime access local or appropriately protected. Estack does not silently install, start, expose, or configure the MCP server. Without Tidewave, normal source inspection, Mix, and tests remain a complete workflow.

## Ash and umbrellas

Detect `ash` and `ash_*` dependencies and inspect resources, actions, domains, and policies. Prefer package-provided guidance and preserve the application's action boundary. Ecto remains relevant underneath many Ash apps, but raw Repo writes can bypass action behavior and authorization.

For umbrellas, inspect every affected child application and shared config. Do not assume one Repo, endpoint, application name, or deployment unit.

## Quality tools

Adopt checks according to the project and use the included configuration as a starting point. Boundary, Oban, Dialyxir, Sobelow, ExCoveralls, and migration checkers are optional integrations, not dependencies of Estack itself. Ensure each configured command exists and its flags match the installed version.

## Enforcement

Skills are agent guidance. Branch protection, token permissions, CI, sandboxing, and server-side authorization enforce boundaries. Keep that distinction visible in implementation and documentation.
