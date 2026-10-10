#!/usr/bin/env python3
"""Install/remove the local pack in temporary projects using the pinned Skills CLI."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd):
    env = dict(os.environ, DISABLE_TELEMETRY="1", DO_NOT_TRACK="1", NO_COLOR="1")
    result = subprocess.run(["npx", "--yes", "skills@1.7.2", *args], cwd=cwd,
                            env=env, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(f"Skills CLI failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
    return result


def main():
    expected = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    for agent, mode in ((agent, mode) for agent in ("cursor", "claude-code", "codex")
                        for mode in ("symlink", "copy")):
        with tempfile.TemporaryDirectory(prefix=f"estack-install-{agent}-") as temp:
            project = Path(temp)
            options = ["--copy"] if mode == "copy" else []
            run(["add", str(ROOT), "--skill", "*", "--agent", agent, "--yes", *options], project)
            client_root = ".claude" if agent == "claude-code" else ".agents"
            for name in expected:
                if not (project / client_root / "skills" / name / "SKILL.md").is_file():
                    raise RuntimeError(f"{agent}/{mode}: missing client entrypoint {name}")
            paths = list(project.rglob("SKILL.md"))
            found = {path.parent.name for path in paths}
            if found != expected:
                raise RuntimeError(f"{agent}: discovered {len(found)} of {len(expected)} skills: {found ^ expected}")
            for path in paths:
                source = ROOT / "skills" / path.parent.name
                if path.read_bytes() != (source / "SKILL.md").read_bytes():
                    raise RuntimeError(f"{agent}: installed content differs: {path}")
                for resource in source.rglob("*"):
                    if not resource.is_file() or "__pycache__" in resource.parts:
                        continue
                    installed = path.parent / resource.relative_to(source)
                    if not installed.is_file() or installed.read_bytes() != resource.read_bytes():
                        raise RuntimeError(f"{agent}: bundled resource missing or changed: {resource}")
            # Only remove the names installed in this isolated project.
            # Universal clients share .agents/skills. Target all clients for these
            # exact names so removal also cleans the shared canonical copy.
            unrelated = project / ".agents/skills/unrelated-existing/SKILL.md"
            unrelated.parent.mkdir(parents=True, exist_ok=True)
            unrelated.write_text("Unrelated project content\n")
            run(["remove", *sorted(expected), "--yes"], project)
            remaining = [p for p in project.rglob("SKILL.md") if p.parent.name in expected]
            if remaining:
                raise RuntimeError(f"{agent}: removal left skill files: {remaining}")
            if unrelated.read_text() != "Unrelated project content\n":
                raise RuntimeError(f"{agent}: removal modified unrelated content")
            print(f"PASS {agent}/{mode}: installed {len(expected)} skills with resources and removed them", flush=True)
    print("Installer smoke tests passed. This does not test interactive editor discovery.")


if __name__ == "__main__":
    main()
