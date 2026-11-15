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
