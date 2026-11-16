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


from javis_public_ci.synthetic_gates import assess_synthetic_brain_stage

# CI-MIGRATION-02: public-only fictional negative/positive coverage.
_FAKE_BRAIN_SHA = "d" * 64  # fixed illustrative data, not a real provenance pin


def fictional_stage(family="readiness", **changes):
    packets = {
        "readiness": dict(window="due", source="verified",
                          producer="complete", pending="present"),
        "routing": dict(event="push", publisher="success", writer_count=1,
                        dispatch_requested=False, credentials_used=False),
        "packet": dict(source_digest=_FAKE_BRAIN_SHA,
                       pending_digest=_FAKE_BRAIN_SHA,
                       archive_digest=_FAKE_BRAIN_SHA,
                       receipt_digest=_FAKE_BRAIN_SHA,
                       new_receipt=True, readback=True, overwrote_existing=False),
        "run_card": dict(event="push", run="success", job="success",
                         step="success", attempt=1, new_archive=True, no_op=False),
        "recovery": dict(change_kind="direct", pending_lineage=False,
                         archive_lineage=False, receipt_linked=True,
                         manual_override=False, recovery_failed=False),
    }
    result = dict(fixture_kind="SYNTHETIC_ONLY", family=family, **packets[family])
    result.update(changes)
    return result


class BrainMigration02SyntheticContracts(unittest.TestCase):
    def assertConsistentOnly(self, packet):
        answer = assess_synthetic_brain_stage(packet)
        self.assertEqual(answer["scenario"],
                         "PUBLIC_SYNTHETIC_STAGE_CONSISTENT_NOT_PRIVATE_PROOF")
        self.assertTrue(answer["public_synthetic_only"])
        for key in ("private_brain_parity_verified", "real_evidence_verified",
                    "operational_execution_allowed", "private_ci_replacement_allowed",
                    "publication_authorized"):
            self.assertFalse(answer[key])

    def assertHeld(self, packet):
        out = assess_synthetic_brain_stage(packet)
        self.assertEqual(out["scenario"], "PUBLIC_SYNTHETIC_STAGE_HOLD")
        self.assertFalse(out["operational_execution_allowed"])

    def assertRejected(self, packet):
        with self.assertRaises(PublicSyntheticInputError):
            assess_synthetic_brain_stage(packet)

    def test_02a_five_fictional_baselines_are_never_operational_proof(self):
        for family in ("readiness", "routing", "packet", "run_card", "recovery"):
            with self.subTest(family=family):
                self.assertConsistentOnly(fictional_stage(family))

    def test_02b_readiness_all_unready_states_hold(self):
        for field, values in {"window": ("early", "unknown"),
                              "source": ("missing", "stale"),
                              "producer": ("missing", "failed"),
                              "pending": ("missing",)}.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assertHeld(fictional_stage("readiness", **{field: value}))

    def test_02c_readiness_invalid_types_and_unsupported_states_reject(self):
        for changes in ({"window": []}, {"source": 0},
                        {"pending": True}, {"producer": "approved"},
                        {"window": "tomorrow"}):
            with self.subTest(changes=changes):
                self.assertRejected(fictional_stage("readiness", **changes))

    def test_02d_routing_denies_skips_duplicate_writers_and_dispatch(self):
        changes = ({"event": "manual"}, {"event": "none"},
                   {"publisher": "failure"}, {"publisher": "skipped"},
                   {"publisher": "running"}, {"writer_count": 0},
                   {"writer_count": 2}, {"writer_count": 10},
                   {"dispatch_requested": True}, {"credentials_used": True})
        for change in changes:
            with self.subTest(change=change):
                self.assertHeld(fictional_stage("routing", **change))

    def test_02e_routing_rejects_unrecognized_or_wrong_type_fields(self):
        changes = ({"event": []}, {"event": "delete"},
                   {"publisher": None}, {"writer_count": True},
                   {"writer_count": -1}, {"writer_count": 11},
                   {"dispatch_requested": 1}, {"credentials_used": "false"})
        for change in changes:
            with self.subTest(change=change):
                self.assertRejected(fictional_stage("routing", **change))

    def test_02f_packet_refuses_digest_drift_and_missing_readback(self):
        changes = ({"pending_digest": "b" * 64},
                   {"archive_digest": "b" * 64},
                   {"receipt_digest": "b" * 64},
                   {"new_receipt": False}, {"readback": False},
                   {"overwrote_existing": True})
        for change in changes:
            with self.subTest(change=change):
                self.assertHeld(fictional_stage("packet", **change))

    def test_02g_packet_requires_only_formatted_fictional_digests(self):
        changes = ({"source_digest": "0"},
                   {"pending_digest": "G" * 64},
                   {"archive_digest": False},
                   {"receipt_digest": []},
                   {"new_receipt": 1},
                   {"readback": "true"},
                   {"overwrote_existing": None})
        for change in changes:
            with self.subTest(change=change):
                self.assertRejected(fictional_stage("packet", **change))

    def test_02h_run_card_requires_all_three_success_levels(self):
        for field in ("run", "job", "step"):
            for state in ("failure", "skipped", "running"):
                with self.subTest(field=field, state=state):
                    self.assertHeld(fictional_stage("run_card", **{field: state}))

    def test_02i_run_card_denies_manual_retry_noop_and_missing_archive(self):
        changes = ({"event": "manual"}, {"event": "none"},
                   {"attempt": 2}, {"attempt": 3},
                   {"no_op": True}, {"new_archive": False})
        for change in changes:
            with self.subTest(change=change):
                self.assertHeld(fictional_stage("run_card", **change))

    def test_02j_run_card_rejects_invalid_attempt_and_unknown_status(self):
        changes = ({"event": 0}, {"event": "dispatch"},
                   {"run": "pending"}, {"job": []},
                   {"step": None}, {"attempt": True},
                   {"attempt": -1}, {"attempt": 11},
                   {"no_op": "yes"}, {"new_archive": 1})
        for change in changes:
            with self.subTest(change=change):
                self.assertRejected(fictional_stage("run_card", **change))

    def test_02k_recovery_follow_on_requires_two_independent_links(self):
        self.assertConsistentOnly(fictional_stage(
            "recovery", change_kind="follow_on",
            pending_lineage=True, archive_lineage=True))
        for field in ("pending_lineage", "archive_lineage"):
            with self.subTest(missing=field):
                change = {"change_kind": "follow_on", "pending_lineage": True,
                          "archive_lineage": True}
                change[field] = False
                self.assertHeld(fictional_stage("recovery", **change))

    def test_02l_recovery_denies_unrelated_and_unsafe_override(self):
        changes = ({"change_kind": "unrelated"},
                   {"receipt_linked": False},
                   {"manual_override": True},
                   {"recovery_failed": True})
        for change in changes:
            with self.subTest(change=change):
                self.assertHeld(fictional_stage("recovery", **change))

    def test_02m_recovery_rejects_unrecognized_types(self):
        changes = ({"change_kind": "force"},
                   {"change_kind": []},
                   {"pending_lineage": 1},
                   {"archive_lineage": "yes"},
                   {"receipt_linked": None},
                   {"manual_override": 0},
                   {"recovery_failed": []})
        for change in changes:
            with self.subTest(change=change):
                self.assertRejected(fictional_stage("recovery", **change))

    def test_02n_unmarked_and_unknown_families_fail_closed(self):
        self.assertRejected(fictional_stage("readiness", fixture_kind="PRIVATE"))
        self.assertRejected({"fixture_kind": "SYNTHETIC_ONLY", "family": "other"})
        self.assertRejected({"fixture_kind": "SYNTHETIC_ONLY", "family": []})
        self.assertRejected([])
        self.assertRejected(None)

    def test_02o_unreviewed_fields_and_cross_family_data_fail_closed(self):
        self.assertRejected(fictional_stage("readiness", secret="dummy"))
        self.assertRejected(fictional_stage("routing", raw_log="fake"))
        self.assertRejected(fictional_stage("packet", access_token="dummy"))
        self.assertRejected(fictional_stage("run_card", actor_name="anonymous"))
        self.assertRejected(fictional_stage("recovery", private_sha="dummy"))
        self.assertRejected(fictional_stage("readiness", event="push"))
        self.assertRejected(fictional_stage("run_card", source_digest="d" * 64))
        self.assertRejected({"fixture_kind": "SYNTHETIC_ONLY", "family": "packet"})
