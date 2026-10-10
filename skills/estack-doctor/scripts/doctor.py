#!/usr/bin/env python3
"""Read-only, dependency-free inventory of a Mix project. Never evaluate project code."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 1_048_576
PACKAGES = (
    "phoenix", "phoenix_live_view", "ecto", "ecto_sql", "postgrex", "ecto_sqlite3",
    "oban", "ash", "ash_postgres", "ash_phoenix", "boundary", "credo", "dialyxir",
    "sobelow", "excoveralls", "mix_audit", "excellent_migrations", "usage_rules",
    "tidewave", "mox", "bypass", "req", "stream_data", "tailwind",
)


def read_text(path: Path, root: Path, warnings: list[str]) -> str:
    """Read bounded regular files without following project-internal symlinks."""
    try:
        for candidate in (path, *path.parents):
            if candidate.is_relative_to(root) and candidate.is_symlink():
                warnings.append(f"Skipped symbolic link: {path.relative_to(root)}")
                return ""
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            warnings.append(f"Skipped path outside project: {path.relative_to(root)}")
            return ""
        if not resolved.is_file():
            return ""
        if resolved.stat().st_size > MAX_BYTES:
            warnings.append(f"Skipped oversized file: {path.relative_to(root)}")
            return ""
        return resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        warnings.append(f"Could not read {path.name}: {type(error).__name__}")
        return ""


def inspect_project(project: Path) -> dict:
    try:
        root = project.resolve()
    except (OSError, RuntimeError) as error:
        raise ValueError("The project directory could not be resolved.") from error
    if not root.is_dir() or not (root / "mix.exs").is_file():
        raise ValueError("Choose a project directory containing mix.exs.")
    warnings: list[str] = []
    root_mix = read_text(root / "mix.exs", root, warnings)
    if not root_mix:
        raise ValueError("The project mix.exs could not be read safely.")
    candidates = [root / "mix.exs"]
    candidates += sorted(root.glob("apps/*/mix.exs"))
    mixes = {str(path.parent.relative_to(root)): read_text(path, root, warnings)
             for path in candidates}
    mix_text = "\n".join(mixes.values())
    lock = read_text(root / "mix.lock", root, warnings)
    packages: dict[str, dict] = {}
    for package in PACKAGES:
        hex_match = re.search(
            rf'["\']?{re.escape(package)}["\']?\s*:\s*\{{:hex,\s*:[\w]+,\s*"([^"\n]+)"',
            lock,
        )
        lock_present = bool(re.search(rf'"{re.escape(package)}"\s*:', lock))
        declared = bool(re.search(rf'\{{\s*:{re.escape(package)}\s*[,}}]', mix_text))
        if hex_match or lock_present or declared:
            packages[package] = {
                "locked_version": hex_match.group(1) if hex_match else None,
                "declared_in_mix": declared,
                "evidence": "lockfile" if hex_match or lock_present else "mix.exs hint",
            }
    applications = []
    for path, content in mixes.items():
        app = re.search(r'\bapp:\s*:([a-zA-Z0-9_]+)', content)
        applications.append({"path": path, "app_name_hint": app.group(1) if app else None})
    configs = []
    for base in [root] + [path.parent for path in candidates[1:]]:
        for relative in ("config/config.exs", "config/test.exs", "assets/css/app.css"):
            # Fixed paths only; never inspect .env or arbitrary secret files.
            configs.append(read_text(base / relative, root, warnings))
    config_text = "\n".join(configs)
    instruction_files = [str(p.relative_to(root)) for p in
                         [root / "AGENTS.md", root / "CLAUDE.md"] if p.is_file()]
    pins = [name for name in (".tool-versions", "mise.toml", ".mise.toml", ".elixir-version")
            if (root / name).is_file()]
    findings = []
    aliases = [name for name in ("verify", "precommit")
               if re.search(rf'(?:\b{name}|"{name}")\s*:', mix_text)]
    if not aliases:
        findings.append({"priority": "consider", "item": "No standard gate alias detected",
                         "next_step": "Inspect aliases and CI; preserve any differently named gate."})
    if not pins:
        findings.append({"priority": "consider", "item": "No common toolchain pin file detected",
                         "next_step": "Check CI/container pins before adding another source of truth."})
    if not instruction_files:
        findings.append({"priority": "consider", "item": "No root AGENTS.md or CLAUDE.md detected",
                         "next_step": "Check other/nested client instructions before creating one."})
    if "ash" in packages:
        findings.append({"priority": "adapt", "item": "Ash dependency detected",
                         "next_step": "Inspect resources/actions/policies before using raw Repo patterns."})
    if "daisyui" in config_text.lower():
        findings.append({"priority": "preserve", "item": "daisyUI configuration detected",
                         "next_step": "Reuse the existing components, themes, and styling conventions."})
    return {
        "project": str(root), "mode": "static-read-only", "applications": applications,
        "packages": packages, "gate_alias_hints": aliases, "toolchain_files": pins,
        "root_instruction_files": instruction_files,
        "ci_workflows_present": any((root / ".github/workflows").glob("*.y*ml")),
        "findings": findings, "warnings": warnings,
        "limits": ["No project code, tests, services, or migrations were executed.",
                   "Regex-based detection can miss computed configuration or match comments.",
                   "A locked dependency may be transitive or disabled; inspect actual usage.",
                   "This inventory is not a security audit or an agent-client discovery test."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    try:
        report = inspect_project(args.project)
    except ValueError as error:
        print(f"estack-doctor: {error}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"Estack doctor: {report['project']} (static, read-only)")
        for app in report["applications"]:
            print(f"Application: {app['path']} ({app['app_name_hint'] or 'name not detected'})")
        for name, details in report["packages"].items():
            print(f"Dependency: {name} {details['locked_version'] or '(version unknown)'}")
        for finding in report["findings"]:
            print(f"[{finding['priority']}] {finding['item']}: {finding['next_step']}")
        for warning in report["warnings"]:
            print(f"Warning: {warning}")
        for limit in report["limits"]:
            print(f"Limit: {limit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
