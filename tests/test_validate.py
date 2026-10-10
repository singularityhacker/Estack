"""Negative cases for the release package gate."""
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import validate


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("skills", "docs", ".cursor-plugin", ".claude-plugin"):
            shutil.copytree(ROOT / name, self.root / name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md", "AGENTS.md", "LICENSE"):
            shutil.copy2(ROOT / name, self.root / name)

    def test_complete_package_passes(self):
        self.assertEqual([], validate(self.root))

    def test_missing_installed_resource_fails(self):
        (self.root / "skills/estack-quality/assets/discarded_result.ex").unlink()
        self.assertTrue(any("invalid local link" in e for e in validate(self.root)))

    def test_valid_repo_link_cannot_escape_installable_skill(self):
        path = self.root / "skills/estack-doctor/SKILL.md"
        path.write_text(path.read_text() + "\n[Required guide](../../README.md)\n")
        self.assertTrue(any("outside its installable skill" in e for e in validate(self.root)))

    def test_stale_catalog_fails(self):
        path = self.root / "README.md"
        path.write_text(path.read_text().replace("Inspect an Elixir/Phoenix project's setup", "Outdated description"))
        self.assertTrue(any("catalog is stale" in e for e in validate(self.root)))

    def test_mismatched_ui_invocation_fails(self):
        path = self.root / "skills/estack-doctor/agents/openai.yaml"
        path.write_text(path.read_text().replace("$estack-doctor", "$wrong-skill"))
        self.assertTrue(any("default prompt must invoke" in e for e in validate(self.root)))


if __name__ == "__main__":
    unittest.main()
