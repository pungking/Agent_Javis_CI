import unittest

from javis_public_ci.contracts import (
    Notice, candidate_union, validate_source_statuses,
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


if __name__ == "__main__":
    unittest.main()
