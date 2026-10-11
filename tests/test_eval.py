"""Protocol regression tests; model calls and Elixir are not needed here."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("estack_eval", ROOT / "skills/estack-eval/scripts/eval.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class EvaluationProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.case = ROOT / "evals/cases/tenant-boundary"
        self.run = self.root / "control"
        self.manifest = runner.prepare(self.case, "none", ROOT / "skills", self.run,
                                       self.root / "projects", repeats=2)

    def test_pairs_share_request_and_fixture_without_exposing_grader(self):
        self.assertEqual(4, len(self.manifest["workers"]))
        for pair in (1, 2):
            workers = [w for w in self.manifest["workers"] if w["pair"] == pair]
            self.assertEqual({"baseline", "candidate"}, {w["condition"] for w in workers})
            requests = [(Path(w["workspace"]) / "REQUEST.md").read_bytes() for w in workers]
            self.assertEqual(requests[0], requests[1])
            for worker in workers:
                names = runner.inventory(Path(worker["workspace"]))
                self.assertFalse(any("grader" in p or "rubric" in p or "manifest" in p for p in names))
                self.assertEqual(worker["condition"] == "candidate", bool(worker["instructions"]))

    def test_cannot_overwrite_existing_run(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            runner.prepare(self.case, "none", "none", self.run, self.root / "projects")

    def test_outputs_cannot_recursively_copy_their_source(self):
        import shutil
        source = self.root / "source"
        shutil.copytree(self.case, source)
        with self.assertRaisesRegex(ValueError, "outside case and skill sources"):
            runner.prepare(source, "none", "none", source / "nested", self.root / "projects")
        self.assertFalse((source / "nested").exists())

    def test_changed_frozen_case_is_rejected(self):
        (self.run / "case/task.md").write_text("Different task")
        with self.assertRaisesRegex(ValueError, "Frozen case changed"):
            runner.load_run(self.run)

    def test_worker_cannot_edit_existing_tests_or_instructions(self):
        worker = self.manifest["workers"][0]
        (Path(worker["workspace"]) / "test/smoke.exs").write_text("weakened test")
        _, problems = runner.artifact(worker, runner.load_case(self.case))
        self.assertEqual(["Changed protected path: test/smoke.exs"], problems)

    def test_symlink_submission_is_rejected(self):
        worker = self.manifest["workers"][0]
        path = Path(worker["workspace"]) / "lib/invoices.ex"
        path.unlink()
        path.symlink_to(self.root / "outside")
        with self.assertRaisesRegex(ValueError, "Symbolic links"):
            runner.artifact(worker, runner.load_case(self.case))

    def test_missing_worker_is_not_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, "Record every worker"):
            runner.grade(self.run)

    def test_incomplete_grading_cannot_turn_coordinator_state_into_a_worker_failure(self):
        for worker in self.manifest["workers"]:
            runner.record(self.run, worker["id"], "completed")
        (self.run / "artifacts").mkdir()
        with self.assertRaisesRegex(ValueError, "Incomplete grading"):
            runner.grade(self.run)
        self.assertFalse((self.run / "grades.json").exists())

    def test_missing_runtime_does_not_freeze_invalid_scores(self):
        for worker in self.manifest["workers"]:
            runner.record(self.run, worker["id"], "completed")
        with patch.object(runner.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "no scores were written"):
                runner.grade(self.run)
        self.assertFalse((self.run / "grades.json").exists())
        self.assertFalse((self.run / "artifacts").exists())

    def test_metrics_must_be_finite(self):
        for value in (float("nan"), float("inf"), -1, True):
            with self.assertRaisesRegex(ValueError, "nonnegative or unknown"):
                runner.record(self.run, self.manifest["workers"][0]["id"], "completed", cost=value)

    def test_timeouts_remain_in_denominator_with_unknown_metrics(self):
        for worker in self.manifest["workers"]:
            runner.record(self.run, worker["id"], "timeout")
        self.assertEqual(4, len(runner.grade(self.run)))
        report = runner.report(self.run)
        self.assertEqual(4, len(report["rows"]))
        self.assertTrue(all(not row["eligible"] for row in report["rows"]))
        self.assertTrue(all(row["record"]["tokens"] is None for row in report["rows"]))
        with self.assertRaisesRegex(ValueError, "already exist"):
            runner.grade(self.run)

    def test_grader_repairs_preserve_old_case_and_cannot_change_rubric(self):
        import shutil
        revision = self.root / "revision"
        shutil.copytree(self.case, revision)
        (revision / "grader/verify.exs").write_text("# driver repair\n")
        runner.amend_grader(self.run, revision, "Driver failed to compile")
        _, manifest, _ = runner.load_run(self.run)
        self.assertEqual(1, len(manifest["amendments"]))
        self.assertTrue((self.run / "amendments/1/case/grader/verify.exs").is_file())
        (revision / "task.md").write_text("New task")
        with self.assertRaisesRegex(ValueError, "cannot be amended"):
            runner.amend_grader(self.run, revision, "Changed task")

    def test_grader_schema_and_exit_status_must_agree(self):
        case = runner.load_case(self.case)
        checks = [{"id": c["id"], "passed": True, "detail": "passed"} for c in case["checks"]]
        output = runner.RESULT_PREFIX + json.dumps({"checks": checks})
        self.assertEqual(checks, runner.parse_checks(output, 0, case))
        with self.assertRaisesRegex(ValueError, "contradicts"):
            runner.parse_checks(output, 1, case)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            runner.parse_checks(output + "\n" + output, 0, case)

    def test_judge_cannot_prefer_a_critical_failure(self):
        case = runner.load_case(self.case)
        mapping = {"pair-01": {"A": "one", "B": "two"}}
        grades = {"one": {"eligible": False}, "two": {"eligible": True}}
        scores = {label: {r["id"]: {"score": 2, "evidence": "Observed code behavior"} for r in case["rubric"]} for label in ("A", "B")}
        judgment = {"schema_version": 1, "judgments": [{"pair_id": "pair-01", "scores": scores, "preference": "A", "rationale": "Looks cleaner"}]}
        with self.assertRaisesRegex(ValueError, "contradicts critical"):
            runner.validate_judgment(judgment, mapping, case, grades)
        judgment["judgments"][0]["preference"] = "B"
        self.assertEqual(1, len(runner.validate_judgment(judgment, mapping, case, grades)))
        judgment["judgments"][0]["scores"]["A"]["clarity"]["evidence"] = ""
        with self.assertRaisesRegex(ValueError, "supporting evidence"):
            runner.validate_judgment(judgment, mapping, case, grades)


if __name__ == "__main__":
    unittest.main()
