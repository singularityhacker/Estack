#!/usr/bin/env python3
"""Generate the README catalog from the actual skill metadata."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
START, END = "<!-- catalog:start -->", "<!-- catalog:end -->"


def metadata(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError(f"{path}: missing frontmatter")
    result = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if not sep or key in result or key not in ("name", "description"):
            raise ValueError(f"{path}: expected unique name/description scalar fields")
        result[key] = value.strip()
    if set(result) != {"name", "description"} or not all(result.values()):
        raise ValueError(f"{path}: name and description are required")
    return result


def catalog(root=ROOT):
    rows = ["| Skill | Purpose |", "|---|---|"]
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        meta = metadata(path)
        purpose = meta["description"].split(". Use ")[0].rstrip(".")
        purpose = purpose.replace("|", "\\|")
        rows.append(f"| [`{meta['name']}`]({path.relative_to(root).as_posix()}) | {purpose} |")
    return "\n".join(rows)


def updated_readme(root=ROOT):
    text = (root / "README.md").read_text()
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("README must contain exactly one catalog marker pair")
    prefix, rest = text.split(START)
    _, suffix = rest.split(END)
    return prefix + START + "\n" + catalog(root) + "\n" + END + suffix


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    desired = updated_readme()
    if args.check:
        if desired != (ROOT / "README.md").read_text():
            raise SystemExit("README catalog is stale; run python3 scripts/catalog.py")
        print("Skill catalog is current")
    else:
        (ROOT / "README.md").write_text(desired)
        print("Updated skill catalog")
