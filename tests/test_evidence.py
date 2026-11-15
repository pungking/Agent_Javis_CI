"""Synthetic negative tests: a public workflow NEVER validates private Javis code."""
import unittest

from javis_public_ci.evidence import EvidenceHold, evaluate_public_ci

SHA = "a" * 40


def fixture():
    run = {
        "repository": {"full_name": "pungking/Agent_Javis_CI"},
        "head_sha": SHA,
        "event": "pull_request",
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
        "id": 123456,
    }
    jobs = [
        {"id": 1001, "name": "Synthetic contracts Python 3.11",
         "status": "completed", "conclusion": "success"},
        {"id": 1002, "name": "Synthetic contracts Python 3.12",
         "status": "completed", "conclusion": "success"},
    ]
    return run, jobs


class PublicEvidenceBoundary(unittest.TestCase):
    def test_01_synthetic_only_and_no_private_promotion(self):
        run, jobs = fixture()
        result = evaluate_public_ci(run, jobs, expected_sha=SHA)
        self.assertEqual(result["state"], "PUBLIC_SYNTHETIC_JOBS_OBSERVED_SUCCESS")
        self.assertFalse(result["private_agent_javis_source_tested"])
        self.assertFalse(result["private_agent_javis_brain_source_tested"])
        self.assertFalse(result["private_source_ci_promotable"])
        self.assertFalse(result["log_level_test_count_verified"])
        self.assertFalse(result["github_api_authenticity_checked_here"])

    def test_02_wrong_repository_denied(self):
        run, jobs = fixture()
        run["repository"]["full_name"] = "pungking/Agent_Javis"
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_03_sha_mismatch_denied(self):
        run, jobs = fixture()
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha="b" * 40)

    def test_04_bad_pin_denied(self):
        run, jobs = fixture()
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha="../../main")

    def test_05_failed_run_denied(self):
        run, jobs = fixture()
        run["conclusion"] = "failure"
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_06_rerun_denied_until_review(self):
        run, jobs = fixture()
        run["run_attempt"] = 2
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_07_dispatch_denied_until_review(self):
        run, jobs = fixture()
        run["event"] = "workflow_dispatch"
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_08_missing_matrix_job_denied(self):
        run, jobs = fixture()
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs[:1], expected_sha=SHA)

    def test_09_failed_job_denied(self):
        run, jobs = fixture()
        jobs[0]["conclusion"] = "skipped"
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_10_duplicate_job_denied(self):
        run, jobs = fixture()
        jobs[1]["name"] = jobs[0]["name"]
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_11_injected_success_not_private_validation(self):
        run, jobs = fixture()
        run["private_agent_javis_source_tested"] = True
        run["private_agent_javis_brain_source_tested"] = True
        result = evaluate_public_ci(run, jobs, expected_sha=SHA)
        self.assertIs(result["private_agent_javis_source_tested"], False)
        self.assertIs(result["private_agent_javis_brain_source_tested"], False)

    def test_12_invalid_job_id_denied(self):
        run, jobs = fixture()
        jobs[1]["id"] = True
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_13_invalid_run_id_denied(self):
        run, jobs = fixture()
        run["id"] = False
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_14_non_dict_evidence_denied(self):
        _, jobs = fixture()
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci([], jobs, expected_sha=SHA)

    def test_15_job_status_incomplete_denied(self):
        run, jobs = fixture()
        jobs[0]["status"] = "queued"
        with self.assertRaises(EvidenceHold):
            evaluate_public_ci(run, jobs, expected_sha=SHA)

    def test_16_pr_event_with_public_source_is_still_only_synthetic(self):
        run, jobs = fixture()
        run["event"] = "push"
        result = evaluate_public_ci(run, jobs, expected_sha=SHA)
        self.assertEqual(result["source_scope"], "PUBLIC_SYNTHETIC_ONLY")


if __name__ == "__main__":
    unittest.main()
