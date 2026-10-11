# Sources and attribution

Estack combines the author's production experience with workflow inspiration and upstream technical documentation. Referenced projects do not endorse Estack. Recheck version-sensitive guidance against the application being edited.

## Production experience

Justice Conder's work on [ClawBank](https://clawbank.co) supplied the original context: tenant isolation, vendor-independent development, explicit errors, durable operations, and agent maintenance boundaries.

## Process inspiration named in the original pack

- [Gstack](https://github.com/garrytan/gstack)
- [Pstack](https://github.com/backnotprop/pstack)
- [Matt Pocock's skills](https://github.com/mattpocock/skills)

These links record acknowledged inspiration, not a claim that all current wording was copied from those projects. The prelaunch README also referred to five unnamed Elixir packs; their identities were not recorded in this repository. That unsupported count has been removed. Add precise source/commit attribution when provenance can be established, and retain required notices for any copied code or text.

## Evaluation workflow

The v1.1 evaluation protocol is inspired by [Pstack's Eval playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md), surfaced by [kaito](https://zenn.dev/sc30gsw). Estack implements its own case format, orchestration, Elixir graders, and reports. See [evaluations](evals.md) for measured scope and limitations.

## Technical references

- [Elixir](https://hexdocs.pm/elixir/) and [OTP](https://www.erlang.org/doc/): process, task, and language behavior.
- [Phoenix](https://hexdocs.pm/phoenix/) and [LiveView](https://hexdocs.pm/phoenix_live_view/): scopes, security, forms, components, and releases.
- [Ecto](https://hexdocs.pm/ecto/) and [SQL sandbox](https://hexdocs.pm/ecto_sql/Ecto.Adapters.SQL.Sandbox.html): data integrity and test ownership.
- [Oban](https://hexdocs.pm/oban/): worker results, uniqueness, retries, and testing.
- [Credo](https://hexdocs.pm/credo/) and [ExCoveralls](https://hexdocs.pm/excoveralls/readme.html): check configuration and coverage semantics.
- [UsageRules](https://github.com/ash-project/usage_rules) and [Tidewave Phoenix](https://github.com/tidewave-ai/tidewave_phoenix): complementary agent tools.
- [Agent Skills specification](https://agentskills.io/specification), [Skills CLI](https://github.com/vercel-labs/skills), and client documentation linked from the installation guide.

## A known inherited preference

Phoenix v1.8.0's [generated AGENTS.md](https://github.com/phoenixframework/phoenix/blob/v1.8.0/installer/templates/phx_single/AGENTS.md) favored hand-written Tailwind components over daisyUI for aesthetic reasons. Estack's initial blanket daisyUI prohibition resembled that guidance, although the exact copying chain is unrecorded. v1 removes the ban and preserves the project's chosen UI system. Phoenix itself includes daisyUI support.

## Maintaining provenance

Link each version-sensitive rule to primary documentation where practical. Distinguish a correctness requirement, a recommended default, a project convention, and an environment-specific choice. Include a concrete failure case when strengthening a rule to an absolute.
