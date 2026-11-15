"""Independent public-only fixture tests; no private repository access."""
import unittest

from javis_public_ci.synthetic_gates import (
    PublicSyntheticInputError, assess_synthetic_delivery,
    assess_synthetic_mission,
)

FAKE_HASH = "a" * 64


def sample_delivery(**overrides):
    packet = dict(
        fixture_kind="SYNTHETIC_ONLY",
        scheduled=True, generation_complete=True, pending_present=True,
        writer_event="push", writer_state="success", trigger_kind="direct",
        pending_ancestry=False, archive_ancestry=False, archive_count=1,
        new_draft=True, new_receipt=True,
        source_digest=FAKE_HASH, pending_digest=FAKE_HASH,
        archive_digest=FAKE_HASH, receipt_digest=FAKE_HASH,
        readback_pass=True, no_op=False,
    )
    packet.update(overrides)
    return packet


def sample_mission(**overrides):
    packet = dict(
        fixture_kind="SYNTHETIC_ONLY",
        current_state="DRAFT", next_state="REVIEW",
        human_approved=False, execution_requested=False,
    )
    packet.update(overrides)
    return packet


class PublicOnlyDeliveryContractTests(unittest.TestCase):
    def test_direct_demo_consistent_but_never_private_proof(self):
        out = assess_synthetic_delivery(sample_delivery())
        self.assertEqual(out["scenario"],
                         "PUBLIC_SYNTHETIC_CHAIN_CONSISTENT_NOT_PRIVATE_PROOF")
        self.assertTrue(out["public_synthetic_only"])
        self.assertFalse(out["private_ci_parity_verified"])
        self.assertFalse(out["private_source_executed"])
        self.assertFalse(out["real_writer_or_mac_delivery_verified"])
        self.assertFalse(out["execution_allowed"])

    def test_later_code_demo_requires_two_ancestry_links(self):
        out = assess_synthetic_delivery(sample_delivery(
            trigger_kind="later_code", pending_ancestry=True,
            archive_ancestry=True))
        self.assertEqual(out["scenario"],
                         "PUBLIC_SYNTHETIC_CHAIN_CONSISTENT_NOT_PRIVATE_PROOF")
        for field in ("pending_ancestry", "archive_ancestry"):
            with self.subTest(field=field):
                kwargs = {"trigger_kind": "later_code",
                          "pending_ancestry": True, "archive_ancestry": True}
                kwargs[field] = False
                out = assess_synthetic_delivery(sample_delivery(**kwargs))
                self.assertEqual(out["scenario"], "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_unrelated_trigger_always_holds(self):
        out = assess_synthetic_delivery(sample_delivery(
            trigger_kind="unrelated", pending_ancestry=True,
            archive_ancestry=True))
        self.assertEqual(out["scenario"], "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_writer_failure_skip_running_absent_hold(self):
        for state in ("failure", "skipped", "running", "absent"):
            with self.subTest(state=state):
                out = assess_synthetic_delivery(sample_delivery(writer_state=state))
                self.assertEqual(out["scenario"], "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_noop_and_zero_archive_hold(self):
        for overrides in ({"no_op": True}, {"archive_count": 0}):
            with self.subTest(overrides=overrides):
                self.assertEqual(assess_synthetic_delivery(
                    sample_delivery(**overrides))["scenario"],
                    "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_missing_new_draft_or_receipt_hold(self):
        for field in ("new_draft", "new_receipt"):
            with self.subTest(field=field):
                self.assertEqual(assess_synthetic_delivery(
                    sample_delivery(**{field: False}))["scenario"],
                    "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_digest_or_readback_mismatch_holds(self):
        for kwargs in ({"pending_digest": "b"*64},
                       {"archive_digest": "b"*64},
                       {"receipt_digest": "b"*64},
                       {"readback_pass": False}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(assess_synthetic_delivery(
                    sample_delivery(**kwargs))["scenario"],
                    "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_scheduled_generation_and_pending_absence_holds(self):
        for field in ("scheduled", "generation_complete", "pending_present"):
            with self.subTest(field=field):
                self.assertEqual(assess_synthetic_delivery(
                    sample_delivery(**{field: False}))["scenario"],
                    "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_manual_event_not_natural_push_proof(self):
        self.assertEqual(assess_synthetic_delivery(
            sample_delivery(writer_event="manual"))["scenario"],
            "PUBLIC_SYNTHETIC_CHAIN_HOLD")

    def test_unknown_event_or_trigger_fails_closed(self):
        for kwargs in ({"writer_event": "new_event"},
                       {"writer_state": "unknown"},
                       {"trigger_kind": "unknown"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(PublicSyntheticInputError):
                    assess_synthetic_delivery(sample_delivery(**kwargs))

    def test_malformed_nonhashable_event_fields_fail_closed(self):
        for kwargs in ({"writer_event": []},
                       {"writer_state": {}},
                       {"trigger_kind": []},
                       {"writer_event": 0}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(PublicSyntheticInputError):
                    assess_synthetic_delivery(sample_delivery(**kwargs))

    def test_secret_or_private_raw_evidence_key_rejected(self):
        for kwargs in ({"token": "not-a-real-token"},
                       {"raw_markdown": "not-real"},
                       {"operational_log": "not-real"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(PublicSyntheticInputError):
                    assess_synthetic_delivery(sample_delivery(**kwargs))

    def test_non_synthetic_input_and_bad_shape_rejected(self):
        with self.assertRaises(PublicSyntheticInputError):
            assess_synthetic_delivery(sample_delivery(fixture_kind="REAL"))
        with self.assertRaises(PublicSyntheticInputError):
            assess_synthetic_delivery({"fixture_kind": "SYNTHETIC_ONLY"})
        with self.assertRaises(PublicSyntheticInputError):
            assess_synthetic_delivery([])

    def test_bad_sha_boolean_or_archive_count_rejected(self):
        for kwargs in ({"source_digest": "fake"},
                       {"pending_digest": "g"*64},
                       {"archive_count": True},
                       {"archive_count": -1},
                       {"scheduled": "yes"},
                       {"archive_count": 101}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(PublicSyntheticInputError):
                    assess_synthetic_delivery(sample_delivery(**kwargs))


class PublicOnlyMissionContractTests(unittest.TestCase):
    def test_draft_to_review_is_only_synthetic(self):
        out = assess_synthetic_mission(sample_mission())
        self.assertEqual(out["scenario"], "PUBLIC_SYNTHETIC_REVIEW_TRANSITION")
        self.assertFalse(out["private_core_policy_verified"])
        self.assertFalse(out["executor_invoked"])
        self.assertFalse(out["real_approval_authenticated"])
        self.assertFalse(out["operational_execution_allowed"])

    def test_review_to_approved_requires_explicit_boolean(self):
        out = assess_synthetic_mission(sample_mission(
            current_state="REVIEW", next_state="APPROVED", human_approved=True))
        self.assertEqual(out["scenario"], "PUBLIC_SYNTHETIC_REVIEW_TRANSITION")
        hold = assess_synthetic_mission(sample_mission(
            current_state="REVIEW", next_state="APPROVED"))
        self.assertEqual(hold["scenario"], "PUBLIC_SYNTHETIC_DENY")

    def test_actual_execution_never_authorized(self):
        for next_state in ("EXECUTING", "APPROVED"):
            with self.subTest(next_state=next_state):
                out = assess_synthetic_mission(sample_mission(
                    current_state="REVIEW", next_state=next_state,
                    human_approved=True, execution_requested=True))
                self.assertEqual(out["scenario"], "PUBLIC_SYNTHETIC_DENY")
                self.assertFalse(out["operational_execution_allowed"])

    def test_illegal_transitions_hold(self):
        for current, nxt in (
            ("DRAFT", "APPROVED"), ("REJECTED", "APPROVED"),
            ("APPROVED", "DRAFT"), ("REVIEW", "DRAFT"),
        ):
            with self.subTest(current=current, nxt=nxt):
                result = assess_synthetic_mission(sample_mission(
                    current_state=current, next_state=nxt, human_approved=True))
                self.assertEqual(result["scenario"], "PUBLIC_SYNTHETIC_DENY")

    def test_malformed_nonhashable_mission_states_fail_closed(self):
        for kwargs in ({"current_state": []}, {"next_state": {}},
                       {"current_state": 1}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(PublicSyntheticInputError):
                    assess_synthetic_mission(sample_mission(**kwargs))

    def test_unknown_or_unmarked_mission_is_rejected(self):
        for overrides in ({"current_state": "OPEN"}, {"next_state": "OPEN"},
                          {"fixture_kind": "PRIVATE"},
                          {"human_approved": 1},
                          {"secret": "synthetic-only"}):
            with self.subTest(overrides=overrides):
                with self.assertRaises(PublicSyntheticInputError):
                    assess_synthetic_mission(sample_mission(**overrides))


if __name__ == "__main__":
    unittest.main()
