import unittest

from javis_public_ci.contracts import (
    Notice, candidate_union, validate_source_statuses,
    assess_public_synthetic_candidate,
)

URLS = {
    "IRIS": "https://www.iris.go.kr/main.do",
    "SMTECH": "https://www.smtech.go.kr/front/main/main.do",
    "SROME": "https://srome.keit.re.kr/srome/sromeIndex.do",
}


def notice(source, notice_id="2027-01", authority="Synthetic Agency"):
    return Notice(source, authority, notice_id, "Synthetic R&D opportunity", URLS[source])


class IndependentDiscovery(unittest.TestCase):
    def test_01_iris_only_is_candidate(self):
        self.assertEqual(candidate_union([notice("IRIS")])[0]["source_ids"], ["IRIS"])

    def test_02_smtech_only_is_candidate(self):
        self.assertEqual(candidate_union([notice("SMTECH")])[0]["source_ids"], ["SMTECH"])

    def test_03_srome_only_is_candidate(self):
        self.assertEqual(candidate_union([notice("SROME")])[0]["source_ids"], ["SROME"])

    def test_04_exact_identity_deduplicates_but_retains_sources(self):
        result = candidate_union([notice("IRIS"), notice("SMTECH"), notice("SROME")])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source_ids"], ["IRIS", "SMTECH", "SROME"])
        self.assertEqual(len(result[0]["source_urls"]), 3)

    def test_05_different_ids_do_not_deduplicate(self):
        self.assertEqual(len(candidate_union([notice("IRIS", "1"), notice("IRIS", "2")])), 2)

    def test_06_same_id_different_authority_does_not_deduplicate(self):
        result = candidate_union([notice("IRIS", "1", "Agency A"), notice("SMTECH", "1", "Agency B")])
        self.assertEqual(len(result), 2)

    def test_07_unlisted_portals_do_not_invalidate_discovery(self):
        validate_source_statuses({"IRIS": "FOUND_OFFICIAL", "SMTECH": "NOT_LISTED", "SROME": "NOT_LISTED"})
        self.assertEqual(len(candidate_union([notice("IRIS")])), 1)

    def test_08_unknown_portal_fails_closed(self):
        with self.assertRaises(ValueError):
            Notice("UNKNOWN", "A", "B", "C", "https://example.com/")

    def test_09_offsite_url_fails_closed(self):
        with self.assertRaises(ValueError):
            Notice("IRIS", "A", "B", "C", "https://evil.example.net/")

    def test_10_missing_status_fails_closed(self):
        with self.assertRaises(ValueError):
            validate_source_statuses({"IRIS": "FOUND_OFFICIAL"})

    def test_11_no_implicit_rights_or_submissions(self):
        for result in candidate_union([notice("SROME")]):
            for field in ("eligibility_verified", "planning_ready", "rights_for_ai_reuse_verified", "application_submission_allowed"):
                self.assertIs(result[field], False)

    def test_12_no_items_does_not_fake_candidates(self):
        self.assertEqual(candidate_union([]), [])

    def test_13_invalid_status_fails_closed(self):
        with self.assertRaises(ValueError):
            validate_source_statuses({"IRIS": "FOUND_OFFICIAL", "SMTECH": "SUCCESS", "SROME": "NOT_LISTED"})

    def test_14_fake_userinfo_is_rejected(self):
        with self.assertRaises(ValueError):
            Notice("IRIS", "A", "B", "C", "https://user@www.iris.go.kr/main.do")


def synthetic_release_case():
    return {
        "kind": "SYNTHETIC_CONTRACT",
        "origin": "INDEPENDENT_PUBLIC_AUTHORING",
        "private_source_included": False,
        "private_data_included": False,
        "credentials_included": False,
        "copyright_documents_included": False,
        "operator_content_review_claimed": True,
    }


class PublicSyntheticReleaseGate(unittest.TestCase):
    def _denied(self, key, value):
        record = synthetic_release_case()
        record[key] = value
        with self.assertRaises(ValueError):
            assess_public_synthetic_candidate(record)

    def test_15_reviewed_synthetic_claim_still_does_not_authorize(self):
        result = assess_public_synthetic_candidate(synthetic_release_case())
        self.assertEqual(result["scope"], "PUBLIC_SYNTHETIC_ONLY")
        self.assertFalse(result["public_release_authorized"])
        self.assertFalse(result["private_agent_javis_source_tested"])
        self.assertFalse(result["private_agent_javis_brain_source_tested"])
        self.assertFalse(result["private_pr_merge_gate_passed"])
        self.assertFalse(result["review_claim_independently_verified"])

    def test_16_private_source_denied(self):
        self._denied("private_source_included", True)

    def test_17_private_data_denied(self):
        self._denied("private_data_included", True)

    def test_18_credentials_denied(self):
        self._denied("credentials_included", True)

    def test_19_original_copyrighted_document_denied(self):
        self._denied("copyright_documents_included", True)

    def test_20_unverified_content_denied(self):
        self._denied("operator_content_review_claimed", False)

    def test_21_wrong_origin_denied(self):
        self._denied("origin", "PRIVATE_SOURCE_DERIVED")

    def test_22_wrong_kind_denied(self):
        self._denied("kind", "PRIVATE_TEST")

    def test_23_extra_claim_of_private_ci_pass_denied(self):
        self._denied("private_agent_javis_source_tested", True)

    def test_24_missing_gate_denied(self):
        record = synthetic_release_case()
        del record["credentials_included"]
        with self.assertRaises(ValueError):
            assess_public_synthetic_candidate(record)

    def test_25_weak_non_boolean_leak_false_denied(self):
        self._denied("private_source_included", 0)

    def test_26_weak_non_boolean_human_review_denied(self):
        self._denied("operator_content_review_claimed", 1)

    def test_27_non_dict_denied(self):
        with self.assertRaises(ValueError):
            assess_public_synthetic_candidate([])

    def test_28_submitted_real_pdf_marker_denied(self):
        self._denied("copyright_documents_included", "pending")

    def test_29_never_forges_provider_or_network_evidence(self):
        result = assess_public_synthetic_candidate(synthetic_release_case())
        self.assertEqual(result["network_or_private_repo_requests"], 0)


if __name__ == "__main__":
    unittest.main()
