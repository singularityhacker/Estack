import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/estack-doctor/scripts/doctor.py"
spec = importlib.util.spec_from_file_location("doctor", SCRIPT)
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def test_static_inventory_preserves_umbrella_ash_and_ui_choices(self):
        self.write("mix.exs", 'def project, do: [apps_path: "apps", aliases: [verify: []]]')
        self.write("apps/web/mix.exs", 'def project, do: [app: :web, deps: [{:ash, "~> 3.0"}]]')
        self.write("mix.lock", '%{"phoenix": {:hex, :phoenix, "1.8.0", "hash"}, "ash": {:git, "url", "sha", []}}')
        self.write("apps/web/assets/css/app.css", '@plugin "../vendor/daisyui";')
        self.write(".env", "DO_NOT_READ_ME=private")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        report = doctor.inspect_project(self.root)
        self.assertEqual(report["packages"]["phoenix"]["locked_version"], "1.8.0")
        self.assertIsNone(report["packages"]["ash"]["locked_version"])
        self.assertEqual(len(report["applications"]), 2)
        self.assertIn("verify", report["gate_alias_hints"])
        self.assertTrue(any(f["priority"] == "preserve" for f in report["findings"]))
        self.assertNotIn("private", json.dumps(report))
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_cli_returns_machine_readable_output_without_running_mix_code(self):
        self.write("mix.exs", 'raise "This is deliberately not runnable"')
        result = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.root), "--format", "json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "static-read-only")

    def test_invalid_project_is_a_clear_error(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("mix.exs", result.stderr)

    def test_external_symlink_is_not_read(self):
        self.write("mix.exs", '[]')
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "external"
            target.write_text('%{"phoenix": {:hex, :phoenix, "private", "hash"}}')
            (self.root / "mix.lock").symlink_to(target)
            report = doctor.inspect_project(self.root)
        self.assertNotIn("phoenix", report["packages"])
        self.assertTrue(report["warnings"])

    def test_oversized_lockfile_is_reported(self):
        self.write("mix.exs", '[]')
        self.write("mix.lock", 'x' * (doctor.MAX_BYTES + 1))
        self.assertTrue(doctor.inspect_project(self.root)["warnings"])

    def test_internal_symlink_cannot_read_excluded_env_file(self):
        self.write("mix.exs", '[]')
        self.write(".env", '%{"phoenix": {:hex, :phoenix, "ENV_SENTINEL", "hash"}}')
        (self.root / "mix.lock").symlink_to(".env")
        report = doctor.inspect_project(self.root)
        self.assertNotIn("ENV_SENTINEL", json.dumps(report))
        self.assertNotIn("phoenix", report["packages"])
        self.assertTrue(report["warnings"])

    def test_symlinked_parent_directory_is_skipped(self):
        self.write("mix.exs", '[]')
        self.write("private/config.exs", "# daisyui sentinel")
        (self.root / "config").symlink_to("private", target_is_directory=True)
        report = doctor.inspect_project(self.root)
        self.assertFalse(any(f["priority"] == "preserve" for f in report["findings"]))
        self.assertTrue(report["warnings"])

    def test_self_referencing_symlink_does_not_crash(self):
        self.write("mix.exs", '[]')
        (self.root / "mix.lock").symlink_to("mix.lock")
        report = doctor.inspect_project(self.root)
        self.assertTrue(report["warnings"])


if __name__ == "__main__":
    unittest.main()
