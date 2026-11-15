"""Pure public GitHub Actions evidence boundary: NEVER attests private tests.

Callers must obtain run/jobs from an independently authenticated GitHub read
operation. This function checks shape/invariants, NOT API authenticity.
No network, no filesystem access, no tokens, no external provider.
"""
from __future__ import annotations

import re

SCHEMA = "javis.public_ci.evidence_boundary.v1"
REPO = "pungking/Agent_Javis_CI"
JOB_NAMES = frozenset({
    "Synthetic contracts Python 3.11",
    "Synthetic contracts Python 3.12",
})
HEX40 = re.compile(r"[0-9a-f]{40}\Z")


class EvidenceHold(ValueError):
    """Fail-closed synthetic evidence assessment."""


def evaluate_public_ci(run: dict, jobs: list[dict], *, expected_sha: str) -> dict:
    """Return a PUBLIC_ONLY report, never a verdict on private sources.

    All run/job fields are treated as untrusted until cross-read by a reviewer
    using the official API, with expected_sha pinned independently.
    """
    if not isinstance(expected_sha, str) or not HEX40.fullmatch(expected_sha):
        raise EvidenceHold("EXPECTED_PIN_FORMAT_HOLD")
    if not isinstance(run, dict) or not isinstance(jobs, list):
        raise EvidenceHold("EVIDENCE_STRUCTURE_HOLD")
    repository = run.get("repository")
    if not isinstance(repository, dict) or repository.get("full_name") != REPO:
        raise EvidenceHold("REPOSITORY_IDENTITY_HOLD")
    if run.get("head_sha") != expected_sha:
        raise EvidenceHold("HEAD_PIN_MISMATCH_HOLD")
    if run.get("event") not in ("push", "pull_request"):
        raise EvidenceHold("UNREVIEWED_EVENT_HOLD")
    if (run.get("status") != "completed"
            or run.get("conclusion") != "success"):
        raise EvidenceHold("INCOMPLETE_OR_FAILED_RUN_HOLD")
    attempt = run.get("run_attempt")
    if type(attempt) is not int or attempt != 1:
        raise EvidenceHold("UNREVIEWED_RUN_ATTEMPT_HOLD")
    run_id = run.get("id")
    if type(run_id) is not int or run_id <= 0:
        raise EvidenceHold("UNREVIEWED_RUN_ID_HOLD")
    if len(jobs) != len(JOB_NAMES):
        raise EvidenceHold("JOB_CARDINALITY_HOLD")

    names: set[str] = set()
    for job in jobs:
        if not isinstance(job, dict):
            raise EvidenceHold("JOB_STRUCTURE_HOLD")
        name = job.get("name")
        if not isinstance(name, str) or name not in JOB_NAMES or name in names:
            raise EvidenceHold("UNEXPECTED_OR_DUPLICATE_JOB_HOLD")
        names.add(name)
        if (job.get("status") != "completed"
                or job.get("conclusion") != "success"):
            raise EvidenceHold("JOB_NOT_SUCCESSFUL_HOLD")
        job_id = job.get("id")
        if type(job_id) is not int or job_id <= 0:
            raise EvidenceHold("JOB_ID_HOLD")
    if names != JOB_NAMES:
        raise EvidenceHold("EXPECTED_MATRIX_MISSING_HOLD")
    return {
        "schema": SCHEMA,
        "state": "PUBLIC_SYNTHETIC_JOBS_OBSERVED_SUCCESS",
        "repository": REPO,
        "head_sha": expected_sha,
        "run_id": run_id,
        "run_attempt": attempt,
        "job_names": sorted(names),
        "source_scope": "PUBLIC_SYNTHETIC_ONLY",
        "private_agent_javis_source_tested": False,
        "private_agent_javis_brain_source_tested": False,
        "private_source_ci_promotable": False,
        "log_level_test_count_verified": False,
        "report_is_signed_attestation": False,
        "github_api_authenticity_checked_here": False,
        "external_provider_calls": 0,
    }
