#!/usr/bin/env python3
"""Validate Estack metadata, manifests, packaged resources, and local links."""
import json
from pathlib import Path
import re
import sys

from catalog import metadata, updated_readme

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    errors = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    names = set()
    for path in skills:
        relative = path.relative_to(root)
        try:
            meta = metadata(path)
        except (ValueError, UnicodeError) as error:
            errors.append(str(error))
            continue
        name = meta["name"]
        if not re.fullmatch(r"estack-[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append(f"{relative}: invalid namespaced name {name}")
        if name != path.parent.name or name in names:
            errors.append(f"{relative}: duplicate or mismatched skill name")
        names.add(name)
        if len(meta["description"]) > 1024 or ": " in meta["description"]:
            errors.append(f"{relative}: description must be a valid short plain YAML scalar")
        content = path.read_text()
        if len(content.splitlines()) > 500:
            errors.append(f"{relative}: move long reference material out of SKILL.md")
        if re.search(r"\bTODO\b|clawbank\.(check_toolchain|quality_report)|No daisyUI", content):
            errors.append(f"{relative}: unresolved scaffold or obsolete instruction")
        ui_path = path.parent / "agents/openai.yaml"
        try:
            lines = ui_path.read_text().splitlines()
            if not lines or lines[0] != "interface:":
                raise ValueError("expected interface metadata")
            ui = {}
            for line in lines[1:]:
                key, value = line.strip().split(": ", 1)
                ui[key] = json.loads(value)
            if not isinstance(ui["display_name"], str) or not ui["display_name"]:
                raise ValueError("missing display name")
            if not 25 <= len(ui["short_description"]) <= 64:
                raise ValueError("short description must contain 25–64 characters")
            if f"${name}" not in ui["default_prompt"]:
                raise ValueError("default prompt must invoke this skill")
        except (OSError, KeyError, ValueError, TypeError) as error:
            errors.append(f"{ui_path.relative_to(root)}: {error}")
    if not skills:
        errors.append("No skills found")
    router = root / "skills/estack-mode/SKILL.md"
    if router.is_file():
        for name in names - {"estack-mode"}:
            if f"`{name}`" not in router.read_text():
                errors.append(f"Router is missing {name}")
    versions = []
    for name in (".cursor-plugin", ".claude-plugin"):
        path = root / name / "plugin.json"
        try:
            data = json.loads(path.read_text())
            versions.append(data["version"])
            if data["name"] != "estack" or data["homepage"] != "https://github.com/singularityhacker/Estack":
                errors.append(f"{path.relative_to(root)}: incorrect identity")
            if not re.fullmatch(r"\d+\.\d+\.\d+", data["version"]):
                errors.append(f"{path.relative_to(root)}: invalid version")
            if name == ".cursor-plugin" and data.get("skills") != "./skills/":
                errors.append("Cursor manifest must reference the canonical skills directory")
        except (OSError, KeyError, ValueError) as error:
            errors.append(f"{path.relative_to(root)}: {error}")
    if len(set(versions)) != 1:
        errors.append("Plugin versions differ")
    readme = (root / "README.md").read_text()
    if readme != updated_readme(root):
        errors.append("README catalog is stale; run python3 scripts/catalog.py")
    count = re.search(r"\*\*(\d+) focused skills\*\*", readme)
    if not count or int(count.group(1)) != len(skills):
        errors.append("README skill count differs from installed catalog")
    # Check all repository Markdown outside dependencies / VCS. No network required.
    paths = [root / "README.md", root / "CONTRIBUTING.md", root / "CHANGELOG.md", root / "AGENTS.md"]
    paths += list((root / "docs").rglob("*.md")) + list((root / "skills").rglob("*.md"))
    for path in paths:
        if not path.is_file():
            errors.append(f"Missing document: {path.relative_to(root)}")
            continue
        text = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
        for link in re.findall(r"\[[^\]\n]+\]\(([^\s)]+)\)", text):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:|#", link):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f"{path.relative_to(root)}: invalid local link {link}")
            elif path.is_relative_to(root / "skills"):
                skill_root = root / "skills" / path.relative_to(root / "skills").parts[0]
                if not target.is_relative_to(skill_root.resolve()):
                    errors.append(f"{path.relative_to(root)}: resource is outside its installable skill: {link}")
    return errors


if __name__ == "__main__":
    errors = validate()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"Validated {len(list((ROOT / 'skills').glob('*/SKILL.md')))} skills, manifests, catalog, and local links")
