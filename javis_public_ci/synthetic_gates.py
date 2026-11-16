"""Public-only illustrative contracts for synthetic CI migration experiments.

This file is an independently authored teaching/test model, NOT a copy or
translation of private source and NOT a production validation implementation.
It cannot attest to private CI, workflows, Git commits, or live delivery.
No IO, network calls, credentials, real events, or private fixture imports.
"""
from __future__ import annotations

import re

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_DELIVERY_FIELDS = frozenset({
    "fixture_kind", "scheduled", "generation_complete", "pending_present",
    "writer_event", "writer_state", "trigger_kind", "pending_ancestry",
    "archive_ancestry", "archive_count", "new_draft", "new_receipt",
    "source_digest", "pending_digest", "archive_digest", "receipt_digest",
    "readback_pass", "no_op",
})
_MISSION_FIELDS = frozenset({
    "fixture_kind", "current_state", "next_state", "human_approved",
    "execution_requested",
})
_ALLOWED_EVENTS = frozenset({"push", "manual", "none"})
_ALLOWED_WRITER_STATES = frozenset({"success", "failure", "skipped", "running", "absent"})
_ALLOWED_TRIGGERS = frozenset({"direct", "later_code", "unrelated"})
_ALLOWED_MISSION_STATES = frozenset({"DRAFT", "REVIEW", "APPROVED", "REJECTED", "EXECUTING"})


class PublicSyntheticInputError(ValueError):
    """Unrecognized, non-synthetic or unsafe fixture schema; fail closed."""


def _shape(packet: object, fields: frozenset[str]) -> None:
    if type(packet) is not dict or set(packet) != fields:
        raise PublicSyntheticInputError("UNREVIEWED_PUBLIC_FIXTURE_FIELDS_HOLD")
    if packet["fixture_kind"] != "SYNTHETIC_ONLY":
        raise PublicSyntheticInputError("REAL_OR_UNMARKED_EVIDENCE_HOLD")


def _boolean(packet: dict, names: tuple[str, ...]) -> None:
    if any(type(packet[name]) is not bool for name in names):
        raise PublicSyntheticInputError("BOOLEAN_CONTRACT_HOLD")


def _digest(value: object) -> None:
    if type(value) is not str or _DIGEST.fullmatch(value) is None:
        raise PublicSyntheticInputError("FAKE_DIGEST_FORMAT_HOLD")


def assess_synthetic_delivery(packet: dict) -> dict:
    """Illustrate strict evidence links; never authorize real delivery.

    This is synthetic contract simulation, NOT W46/W47 source-code parity.
    The digest fields must contain independently generated fake data only.
    """
    _shape(packet, _DELIVERY_FIELDS)
    _boolean(packet, (
        "scheduled", "generation_complete", "pending_present",
        "pending_ancestry", "archive_ancestry", "new_draft",
        "new_receipt", "readback_pass", "no_op",
    ))
    for key in ("source_digest", "pending_digest", "archive_digest", "receipt_digest"):
        _digest(packet[key])
    if type(packet["archive_count"]) is not int or not 0 <= packet["archive_count"] <= 100:
        raise PublicSyntheticInputError("ARCHIVE_COUNT_FORMAT_HOLD")
    if any(type(packet[k]) is not str
           for k in ("writer_event", "writer_state", "trigger_kind")):
        raise PublicSyntheticInputError("EVENT_AND_STATE_TYPE_HOLD")
    if (packet["writer_event"] not in _ALLOWED_EVENTS
            or packet["writer_state"] not in _ALLOWED_WRITER_STATES
            or packet["trigger_kind"] not in _ALLOWED_TRIGGERS):
        raise PublicSyntheticInputError("UNKNOWN_EVENT_OR_STATE_HOLD")
    digests_match = (
        packet["source_digest"] == packet["pending_digest"]
        == packet["archive_digest"] == packet["receipt_digest"]
    )
    direct = packet["trigger_kind"] == "direct"
    recovery = (
        packet["trigger_kind"] == "later_code"
        and packet["pending_ancestry"]
        and packet["archive_ancestry"]
    )
    accepted = all((
        packet["scheduled"], packet["generation_complete"],
        packet["pending_present"], packet["writer_event"] == "push",
        packet["writer_state"] == "success", direct or recovery,
        packet["archive_count"] >= 1, packet["new_draft"],
        packet["new_receipt"], packet["readback_pass"],
        not packet["no_op"], digests_match,
    ))
    return {
        "scenario": (
            "PUBLIC_SYNTHETIC_CHAIN_CONSISTENT_NOT_PRIVATE_PROOF"
            if accepted else "PUBLIC_SYNTHETIC_CHAIN_HOLD"
        ),
        "public_synthetic_only": True,
        "private_source_executed": False,
        "private_ci_parity_verified": False,
        "private_actor_authenticated": False,
        "real_writer_or_mac_delivery_verified": False,
        "execution_allowed": False,
    }


def assess_synthetic_mission(packet: dict) -> dict:
    """Illustrate a fail-closed review transition, not actual agent policy."""
    _shape(packet, _MISSION_FIELDS)
    _boolean(packet, ("human_approved", "execution_requested"))
    if any(type(packet[k]) is not str
           for k in ("current_state", "next_state")):
        raise PublicSyntheticInputError("MISSION_STATE_TYPE_HOLD")
    if (packet["current_state"] not in _ALLOWED_MISSION_STATES
            or packet["next_state"] not in _ALLOWED_MISSION_STATES):
        raise PublicSyntheticInputError("UNKNOWN_MISSION_STATE_HOLD")
    review_step = (
        packet["current_state"] == "DRAFT"
        and packet["next_state"] == "REVIEW"
    )
    approval_step = (
        packet["current_state"] == "REVIEW"
        and packet["next_state"] == "APPROVED"
        and packet["human_approved"]
    )
    permitted = (review_step or approval_step) and not packet["execution_requested"]
    return {
        "scenario": (
            "PUBLIC_SYNTHETIC_REVIEW_TRANSITION" if permitted
            else "PUBLIC_SYNTHETIC_DENY"
        ),
        "public_synthetic_only": True,
        "private_core_policy_verified": False,
        "executor_invoked": False,
        "real_approval_authenticated": False,
        "operational_execution_allowed": False,
    }


# CI-MIGRATION-02: independently authored, PUBLIC SYNTHETIC stages only.
# No actual Brain implementation, original fixture, token, path or Git data.
_BRAIN_STAGE_FIELDS = {
    "readiness": frozenset({"fixture_kind", "family", "window", "source",
                             "producer", "pending"}),
    "routing": frozenset({"fixture_kind", "family", "event", "publisher",
                           "writer_count", "dispatch_requested", "credentials_used"}),
    "packet": frozenset({"fixture_kind", "family", "source_digest",
                          "pending_digest", "archive_digest", "receipt_digest",
                          "new_receipt", "readback", "overwrote_existing"}),
    "run_card": frozenset({"fixture_kind", "family", "event", "run", "job",
                            "step", "attempt", "new_archive", "no_op"}),
    "recovery": frozenset({"fixture_kind", "family", "change_kind",
                            "pending_lineage", "archive_lineage", "receipt_linked",
                            "manual_override", "recovery_failed"}),
}


def assess_synthetic_brain_stage(packet: dict) -> dict:
    """Check original PUBLIC-ONLY fictional scenarios, never real Brain parity.

    A consistent synthetic packet is not permission to run, publish, merge,
    dispatch, authenticate operators, or replace confidential regression.
    """
    if type(packet) is not dict or type(packet.get("family")) is not str:
        raise PublicSyntheticInputError("SYNTHETIC_FAMILY_SCHEMA_HOLD")
    family = packet["family"]
    if family not in _BRAIN_STAGE_FIELDS:
        raise PublicSyntheticInputError("UNKNOWN_SYNTHETIC_FAMILY_HOLD")
    _shape(packet, _BRAIN_STAGE_FIELDS[family])

    if family == "readiness":
        choices = {
            "window": ("due", "early", "unknown"),
            "source": ("verified", "missing", "stale"),
            "producer": ("complete", "failed", "missing"),
            "pending": ("present", "missing"),
        }
        for key, allowed in choices.items():
            if type(packet[key]) is not str or packet[key] not in allowed:
                raise PublicSyntheticInputError("READINESS_FIELD_HOLD")
        consistent = all((packet["window"] == "due",
                          packet["source"] == "verified",
                          packet["producer"] == "complete",
                          packet["pending"] == "present"))
    elif family == "routing":
        for key, allowed in {
            "event": ("push", "manual", "none"),
            "publisher": ("success", "failure", "skipped", "running"),
        }.items():
            if type(packet[key]) is not str or packet[key] not in allowed:
                raise PublicSyntheticInputError("ROUTING_FIELD_HOLD")
        _boolean(packet, ("dispatch_requested", "credentials_used"))
        if type(packet["writer_count"]) is not int or not 0 <= packet["writer_count"] <= 10:
            raise PublicSyntheticInputError("WRITER_COUNT_FIELD_HOLD")
        consistent = all((packet["event"] == "push",
                          packet["publisher"] == "success",
                          packet["writer_count"] == 1,
                          not packet["dispatch_requested"],
                          not packet["credentials_used"]))
    elif family == "packet":
        _boolean(packet, ("new_receipt", "readback", "overwrote_existing"))
        fields = ("source_digest", "pending_digest", "archive_digest", "receipt_digest")
        for key in fields:
            _digest(packet[key])
        consistent = (len({packet[key] for key in fields}) == 1
                      and packet["new_receipt"] and packet["readback"]
                      and not packet["overwrote_existing"])
    elif family == "run_card":
        allowed = {"event": ("push", "manual", "none"),
                   "run": ("success", "failure", "skipped", "running"),
                   "job": ("success", "failure", "skipped", "running"),
                   "step": ("success", "failure", "skipped", "running")}
        for key, values in allowed.items():
            if type(packet[key]) is not str or packet[key] not in values:
                raise PublicSyntheticInputError("RUN_CARD_FIELD_HOLD")
        _boolean(packet, ("new_archive", "no_op"))
        if type(packet["attempt"]) is not int or not 1 <= packet["attempt"] <= 10:
            raise PublicSyntheticInputError("RUN_ATTEMPT_FIELD_HOLD")
        consistent = (packet["event"] == "push"
                      and all(packet[x] == "success" for x in ("run", "job", "step"))
                      and packet["attempt"] == 1 and packet["new_archive"]
                      and not packet["no_op"])
    else:
        if type(packet["change_kind"]) is not str or packet["change_kind"] not in (
                "direct", "follow_on", "unrelated"):
            raise PublicSyntheticInputError("RECOVERY_KIND_FIELD_HOLD")
        _boolean(packet, ("pending_lineage", "archive_lineage", "receipt_linked",
                          "manual_override", "recovery_failed"))
        acceptable_change = (packet["change_kind"] == "direct"
                             or (packet["change_kind"] == "follow_on"
                                 and packet["pending_lineage"]
                                 and packet["archive_lineage"]))
        consistent = (acceptable_change and packet["receipt_linked"]
                      and not packet["manual_override"]
                      and not packet["recovery_failed"])
    return {
        "family": family,
        "scenario": ("PUBLIC_SYNTHETIC_STAGE_CONSISTENT_NOT_PRIVATE_PROOF"
                     if consistent else "PUBLIC_SYNTHETIC_STAGE_HOLD"),
        "public_synthetic_only": True,
        "private_brain_parity_verified": False,
        "real_evidence_verified": False,
        "operational_execution_allowed": False,
        "private_ci_replacement_allowed": False,
        "publication_authorized": False,
    }
