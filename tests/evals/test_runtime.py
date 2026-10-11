"""Exercise trusted graders and the full protocol against known code, without models."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("estack_eval_runtime", ROOT / "skills/estack-eval/scripts/eval.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


@unittest.skipUnless(shutil.which("elixir"), "Elixir 1.18+ is needed for executable calibration")
class RuntimeCalibrationTests(unittest.TestCase):
    def test_each_grader_accepts_reference_and_rejects_seeded_critical_defect(self):
        for case_dir in sorted((ROOT / "evals/cases").iterdir()):
            with self.subTest(case=case_dir.name):
                case = runner.load_case(case_dir)
                grader = case_dir / "grader/verify.exs"
                correct = ROOT / "evals/calibration" / (case_dir.name + ".ex")
                code, output, failure = runner.execute(grader, correct, 20)
                self.assertIsNone(failure)
                results = runner.parse_checks(output, code, case)
                self.assertTrue(all(c["passed"] for c in results))
                code, output, failure = runner.execute(grader, case_dir / "project" / case["editable"][0], 20)
                self.assertIsNone(failure)
                results = runner.parse_checks(output, code, case)
                critical = {c["id"] for c in case["checks"] if c["critical"]}
                self.assertTrue(any(not c["passed"] and c["id"] in critical for c in results))

    def test_round_trip_freezes_code_blinds_judge_and_keeps_failed_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run = root / "control"
            manifest = runner.prepare(ROOT / "evals/cases/tenant-boundary", "none", ROOT / "skills", run, root / "projects")
            for worker in manifest["workers"]:
                if worker["condition"] == "candidate":
                    shutil.copyfile(ROOT / "evals/calibration/tenant-boundary.ex", Path(worker["workspace"]) / "lib/invoices.ex")
                runner.record(run, worker["id"], "completed", model="recorded-model", effort="recorded-effort")
            grades = runner.grade(run)
            self.assertEqual([False, True], sorted(g["eligible"] for g in grades))
            packet = root / "review"
            runner.judge_packet(run, packet)
            text = "\n".join(p.read_text() for p in packet.rglob("*") if p.is_file())
            for worker in manifest["workers"]:
                self.assertNotIn(worker["id"], text)
            self.assertNotIn("recorded-model", text)
            self.assertNotIn("recorded-effort", text)
            self.assertNotIn("estack-ecto", text)
            mapping = runner.read_json(run / "judge-map.json")
            good_id = next(g["id"] for g in grades if g["eligible"])
            good_label = next(label for label, worker in mapping["pair-01"].items() if worker == good_id)
            judgment = runner.read_json(packet / "judgment-template.json")
            entry = judgment["judgments"][0]
            for scores in entry["scores"].values():
                for criterion in scores.values():
                    criterion.update(score=1, evidence="Source and executable checks reviewed")
            entry.update(preference=good_label, rationale="Only one output meets the critical gates")
            runner.write_json(packet / "judgment.json", judgment)
            report = runner.report(run, packet / "judgment.json")
            self.assertEqual(2, len(report["rows"]))
            self.assertEqual(1, len(report["judgments"]))
            # Original project edits after grading cannot change frozen evidence.
            for worker in manifest["workers"]:
                (Path(worker["workspace"]) / "lib/invoices.ex").write_text("changed later")
            self.assertEqual(report, runner.report(run, packet / "judgment.json"))
            entry["rationale"] = "A new opinion after seeing the revealed conditions"
            runner.write_json(packet / "judgment.json", judgment)
            with self.assertRaisesRegex(ValueError, "Judgment is locked"):
                runner.report(run, packet / "judgment.json")
            self.assertEqual(report, runner.report(run))

    def test_timeout_mailbox_leak_fails_even_when_worker_is_stopped(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "submission.ex"
            source.write_text('''defmodule Gateway.VendorRead do
  def run(supervisor, fun, timeout) do
    task = Task.Supervisor.async_nolink(supervisor, fun)
    case Task.yield(task, timeout) do
      {:ok, value} -> {:ok, value}
      {:exit, reason} -> {:error, {:task_exit, reason}}
      nil -> Task.Supervisor.terminate_child(supervisor, task.pid); {:error, :timeout}
    end
  end
end
''')
            case_dir = ROOT / "evals/cases/task-isolation"
            code, output, failure = runner.execute(case_dir / "grader/verify.exs", source, 20)
            self.assertIsNone(failure)
            checks = runner.parse_checks(output, code, runner.load_case(case_dir))
            mailbox = next(c for c in checks if c["id"] == "timeout_mailbox_clean")
            self.assertFalse(mailbox["passed"])

    def test_nonterminating_grader_is_stopped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            grader = root / "driver.exs"
            grader.write_text("Process.sleep(:infinity)\n")
            code, _, failure = runner.execute(grader, grader, 0.3)
            self.assertEqual("grader timeout", failure)
            self.assertNotEqual(0, code)


if __name__ == "__main__":
    unittest.main()
