# Compatibility and validation

Compatibility has several layers: valid files, correct installation, client discovery, and successful application behavior. Estack reports each separately.

## Agent clients

| Client / route | Packaging | Validation in this release |
|---|---|---|
| Cursor through Skills CLI | Standard skills | Installer smoke test in temporary project; interactive editor discovery not tested here |
| Claude Code through Skills CLI | Standard skills | Installer smoke test in temporary project; interactive editor discovery not tested here |
| Codex through Skills CLI | Standard skills plus UI metadata | Installer smoke test in temporary project; interactive editor discovery not tested here |
| Cursor native plugin | `.cursor-plugin/plugin.json` | Manifest/local-path documentation validated; live plugin loading not tested here |
| Claude Code native plugin | `.claude-plugin/plugin.json` | Manifest/local-plugin documentation validated; live plugin loading not tested here |
| Other Agent Skills clients | Portable `SKILL.md` folders | Intended compatibility only; use the client's documented discovery rules |

Installer tests use `skills@1.7.2` with both copy and symlink modes to install all skills/resources and remove them in isolated project directories, preserving unrelated content. The CLI requires Node.js 22.20.0+. These checks do not start the editors, measure model behavior, or validate account/team policies. See the current [CI run](https://github.com/singularityhacker/Estack/actions/workflows/validate.yml) and [hardening report](v1-hardening-report.md) for observed results.

## Elixir/Phoenix applications

Guidance emphasizes modern Phoenix, including 1.8-style scopes/components, while explicitly adapting to existing apps. Read `mix.lock`, toolchain pins, and generated code before applying version-sensitive examples.

- The **helper validation environment** uses Elixir 1.18.4 / OTP 27.3 and Credo 1.7.x.
- It runs the custom Credo check's tests, parses Elixir code fences/assets, and executes selected standalone examples.
- It is not an exhaustive compatibility matrix for Phoenix, LiveView, Ecto, Oban, Ash, hosting platforms, or database adapters.
- No app is required to upgrade its language/framework simply to install Estack's instructions.
- The doctor requires Python 3.10+ and uses only the standard library. Other skills can be used without Python.

## Evaluation support in v1.1

The portable `estack-eval` workflow and Python runner support paired skill/no-skill or version-to-version tasks, frozen artifacts, Elixir behavioral checks, and anonymous reviewer packets. Executable grading requires Elixir 1.18+ on POSIX; CI uses Elixir 1.18.4 / OTP 27.3. Model execution uses the host agent tools and is not automated by the runner. Three public development cases and a small pilot are documented in [evaluations](evals.md). They are not a full Phoenix/database suite or a held-out benchmark.

## What this release does not claim

No public app demo, statistically established agent success-rate improvement, complete Phoenix starter application, production security certification, or verified marketplace approval is included. The initial eval pilot tied and does not establish a benefit from Estack.

A skill instruction is not an enforceable security boundary. A successful source/metadata check does not prove that an agent will follow every rule.
