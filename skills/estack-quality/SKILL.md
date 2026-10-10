---
name: estack-quality
description: Configure and run an Elixir/Phoenix quality gate with honest failure handling. Use for mix verify/precommit, Credo, coverage, Dialyzer, Sobelow, dependency audits, or CI configuration.
---

# The quality wall

Inspect the existing aliases, dependency versions, and CI first. Preserve working gates. Use the project's approved tooling; do not introduce every optional dependency just to match this reference.

## Start with an executable core

The following goes inside the application's Mix project module. Merge it with existing aliases and project settings rather than replacing them:

```elixir
# In project(): preferred_cli_env: [verify: :test, "verify.fast": :test]
# On newer Mix versions, the project may use cli()/preferred_envs instead.
defp aliases do
  [
    "verify.fast": ["format --check-formatted", "compile --warnings-as-errors"],
    verify: ["verify.fast", "test"]
  ]
end
```

Run the core with `MIX_ENV=test mix verify`; develop with focused tests. Before publication, run the full approved gate. Never claim a check ran because its dependency appears in `mix.lock`.

## Add checks intentionally

| Check | Prerequisite / configuration |
|---|---|
| `credo --strict` | Credo dependency and valid `.credo.exs` |
| `coveralls.json --raise` | ExCoveralls, `test_coverage`, test environment, and a configured threshold |
| `dialyzer` | Dialyxir plus appropriate PLT caching |
| `sobelow --config` | Phoenix app, Sobelow, and a reviewed `.sobelow-conf` |
| `deps.audit` | `mix_audit` with a current advisory database |
| `hex.audit` | Hex retired-package check; distinct from vulnerability auditing |
| `excellent_migrations.check_safety` | Compatible migration checker, database assumptions, and reviewed configuration |
| `deps.unlock --check-unused` | Mix version supporting that flag |

Use coverage in place of the ordinary full `test` task if it already runs the same suite, rather than running it twice. Declare the necessary dependencies before adding commands to an alias. There are no required ClawBank-specific Mix tasks.

Verify every selected command's options with `mix help` and the installed version. Configure security exit thresholds deliberately: a stricter threshold must not be described as weakening the gate. Ensure the CI job propagates nonzero exit status.

## Bundled custom check

Copy [discarded_result.ex](assets/discarded_result.ex) to `lib/mix/estack/discarded_result.ex` only if adopting the check. It is guarded so production builds without the dev/test Credo dependency still compile. Merge the relevant configuration from [credo.exs.example](assets/credo.exs.example).

The check flags explicit `_ =` assignments to selected Repo writes, `Oban.insert`, and `Phoenix.PubSub.broadcast`, including a final piped call. Handle expected failures with `case`/`with` or an intentional match. It does not prove all results are handled, infer arbitrary aliases, or flag every unused expression. Configure `repo_modules` for aliases such as `DB`. It deliberately does not flag `_ = Ecto.Multi.new()` as a discarded error: that constructor does not return an error tuple.

## Coverage

Use [coveralls.json.example](assets/coveralls.json.example) as a starting configuration, then choose a project-appropriate `minimum_coverage`. `floor_coverage` controls rounding only. Do not claim per-file thresholds unless the installed tool/config implements them.

Test important authorization, state transitions, errors, and retries regardless of the overall percentage. Establish a realistic baseline for existing code and improve it deliberately.

## Preserve integrity

Fix the finding rather than deleting a check. Explain narrow, reviewed exceptions next to the configuration or code. Legitimate gate repairs are allowed when authorized; avoid adding ignores or exclusions solely to make CI green.

Use the existing toolchain pin (`.tool-versions`, mise, or the project's equivalent) consistently across CI and deployment. Respect formatter/line-length conventions. Cache dependency/PLT artifacts using keys that include relevant toolchain and lockfile changes.

## References

- [Credo configuration](https://hexdocs.pm/credo/config_file.html)
- [ExCoveralls configuration](https://hexdocs.pm/excoveralls/readme.html)
- [Mix aliases](https://hexdocs.pm/mix/Mix.html#module-aliases)
