# Installation

Choose one route per client. Keep the full pack installed so workflow routing can find its domain skills. The Skills CLI version shown here is pinned for reproducible installer behavior; the repository source tracks its current default branch unless you deliberately install a pinned checkout.

## Skills CLI (Cursor, Claude Code, Codex)

With Node.js 22.20.0+ and npm, run from the application repository:

```bash
npx skills@1.7.2 add singularityhacker/Estack --skill '*' --agent cursor
# Alternatives: --agent claude-code or --agent codex
```

Use `--global` for a user-level installation. For automation, add `--yes` to the Skills command after reviewing what will be installed. `npx` may separately ask to download the installer package. You can inspect discovery first:

```bash
npx skills@1.7.2 add singularityhacker/Estack --list
npx skills@1.7.2 list
```

For multiple clients, supply the desired agent names to the CLI. Follow its output for the exact installation locations and any symlinks it creates. Reload/restart the coding client, check the skill list, and invoke `estack-doctor` in a Mix project. A successful file copy does not prove interactive client discovery.

## Native Cursor plugin (without Node.js)

For a new user-level local plugin installation:

```bash
mkdir -p ~/.cursor/plugins/local
git clone https://github.com/singularityhacker/Estack.git ~/.cursor/plugins/local/estack
```

The `.cursor-plugin/plugin.json` manifest must remain at the plugin root. Restart Cursor or run **Developer: Reload Window**, then check **Customize** for Estack's skills. Local plugin imports may be restricted by team/enterprise policy; use an approved installation route rather than bypassing that policy.

Do not clone to `.cursor/plugins/estack` and assume it will load. For project-scoped installation use the Skills CLI or the manual skill-copy route below. Marketplace availability is separate from a local install; this repository does not claim an approved listing.

## Native Claude Code plugin

Clone Estack somewhere outside your application and start Claude Code with the local plugin directory:

```bash
git clone https://github.com/singularityhacker/Estack.git /path/to/Estack
claude --plugin-dir /path/to/Estack
```

Replace `/path/to/Estack` with your actual checkout. Invoke `/estack:estack-doctor`. This route uses `.claude-plugin/plugin.json`; direct Skills CLI installs instead use `/estack-doctor`. Check your installed Claude Code version's local-plugin support. This is a documented packaging route, not a claim of an interactive client test.

## Manual skill copies (without an installer)

Copy each complete `skills/estack-*/` folder into the appropriate directory. Include its `assets/`, `scripts/`, `references/`, and `agents/` when present. Place each skill directly under the skills root; don't copy only the Markdown file.

| Client | Project skill root | Local user skill root |
|---|---|---|
| Cursor | `.cursor/skills/` (also supports `.agents/skills/`) | `~/.cursor/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |

Before copying, check for existing same-name directories. Back up local edits and compare them rather than silently overwriting. To update, replace only the Estack folders you installed. To remove, remove only those folders after preserving local modifications.

## Updates and pinning

For CLI-managed skills, inspect installed entries and use the installer's update/removal commands:

```bash
npx skills@1.7.2 list
npx skills@1.7.2 update
npx skills@1.7.2 remove singularityhacker/Estack
```

Review selection/scope prompts: an unscoped update can include other installed skills. Never run a broad removal command just to uninstall Estack.

The removal command selects the exact source recorded by a GitHub installation and removes those skills from all clients in the selected scope. For local-checkout installs, select the installed `estack-*` names instead (`npx skills@1.7.2 remove` opens the selection prompt). Add `--global` only for a global install. Back up local edits first. Cursor and Codex can share `.agents/skills`; removing from only one client may retain the shared copy for another detected client. Verify the remaining files and skill list after removal.

For native plugin clones, inspect `git status` and local modifications, then run `git pull --ff-only` in the Estack checkout. Reload the client. Remove the dedicated clone to uninstall after preserving your edits.

For a pinned version, clone the repository, check out a reviewed tag or commit, then install from that local checkout using the same CLI (`npx skills@1.7.2 add /path/to/Estack --skill '*' --agent cursor`) or copy its skill folders. Record the commit; updating deliberately changes that pin.

## Cloud agents and team use

A user-local installation is not automatically present on remote workers. Commit project skill files using the client's supported location, or use its approved synchronization/plugin mechanism. Keep portable copies/resources available in the checkout; a symlink to your laptop's absolute path will not work in cloud CI.

Do not install the same pack through both a plugin and direct skill folders in one client. If duplicate names appear, inspect both locations and remove only your redundant Estack installation.

## Prelaunch name migration

v1 namespaces every skill with `estack-`. Existing clones update paths through Git. For old manually copied skills, remove only verified Estack copies after backing up any edits; don't delete another pack's `security` or `deployment` skill merely because its name matches.

| Previous name | v1 name |
|---|---|
| `setup-estack` | `estack-setup` |
| `phoenix-architecture` | `estack-architecture` |
| `liveview-patterns` | `estack-liveview` |
| `ecto-patterns` | `estack-ecto` |
| `oban-patterns` | `estack-oban` |
| `otp-patterns` | `estack-otp` |
| `elixir-idioms` | `estack-elixir` |
| `elixir-testing` | `estack-testing` |
| `elixir-tdd` | `estack-tdd` |
| `quality-wall` | `estack-quality` |
| `elixir-review` | `estack-review` |
| `security` | `estack-security` |
| `deployment` | `estack-deploy` |
| `investigate` | `estack-debug` |
| `agent-safety` | `estack-safety` |
| `estack-mode` | `estack-mode` (unchanged) |

New workflows: `estack-doctor`, `estack-feature`, and `estack-pr`.

## Official client references

- [Cursor skills](https://cursor.com/docs/skills) and [local plugins](https://cursor.com/docs/plugins)
- [Claude Code skills](https://code.claude.com/docs/en/skills) and [plugins](https://code.claude.com/docs/en/plugins)
- [Codex skills](https://developers.openai.com/codex/skills)
- [Skills CLI](https://github.com/vercel-labs/skills)
