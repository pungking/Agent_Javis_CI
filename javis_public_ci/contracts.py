"""Public CI-only contract for independent Korean R&D notice discovery.

This is NOT a mirror of the private Agent_Javis / Agent_Javis_Brain repos.
All inputs in the public repository must be synthetic or otherwise approved for release.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

PORTAL_HOSTS = {
    "IRIS": "www.iris.go.kr",
    "SMTECH": "www.smtech.go.kr",
    "SROME": "srome.keit.re.kr",
}
ALLOWED_SOURCE_STATES = frozenset({
    "FOUND_OFFICIAL", "NOT_LISTED", "ACCESS_RESTRICTED",
    "TEMPORARILY_UNAVAILABLE", "NOT_CHECKED_HOLD",
})

@dataclass(frozen=True)
class Notice:
    source: str
    authority: str
    notice_id: str
    title: str
    source_url: str

    def __post_init__(self):
        if self.source not in PORTAL_HOSTS:
            raise ValueError("UNKNOWN_PORTAL_HOLD")
        if not all(isinstance(v, str) and v.strip() for v in (
            self.authority, self.notice_id, self.title, self.source_url
        )):
            raise ValueError("NOTICE_FIELD_HOLD")
        parsed = urlsplit(self.source_url)
        if (parsed.scheme != "https"
                or parsed.hostname != PORTAL_HOSTS[self.source]
                or parsed.username is not None
                or parsed.password is not None
                or parsed.port not in (None, 443)):
            raise ValueError("OFFICIAL_SOURCE_URL_HOLD")


def candidate_union(notices: list[Notice]) -> list[dict]:
    """Independent source union; never use cross-portal presence as a gate.

    Deduplicate only exact (authority, notice_id), retaining all source links.
    Discovery candidates are never interpreted as verified eligibility or rights.
    """
    grouped: dict[tuple[str, str], list[Notice]] = {}
    for notice in notices:
        if not isinstance(notice, Notice):
            raise TypeError("UNREVIEWED_NOTICE_TYPE_HOLD")
        grouped.setdefault((notice.authority, notice.notice_id), []).append(notice)
    output = []
    for (authority, notice_id), records in sorted(grouped.items()):
        output.append({
            "authority": authority,
            "notice_id": notice_id,
            "source_ids": sorted(set(r.source for r in records)),
            "source_urls": sorted(set(r.source_url for r in records)),
            "state": "DISCOVERY_CANDIDATE_NEEDS_OFFICIAL_RFP_REVIEW",
            "eligibility_verified": False,
            "planning_ready": False,
            "rights_for_ai_reuse_verified": False,
            "application_submission_allowed": False,
        })
    return output


def validate_source_statuses(statuses: dict[str, str]) -> None:
    """Record all three search status values, but require NO shared hits."""
    if set(statuses) != set(PORTAL_HOSTS):
        raise ValueError("MISSING_INDEPENDENT_PORTAL_STATUS_HOLD")
    if not all(state in ALLOWED_SOURCE_STATES for state in statuses.values()):
        raise ValueError("UNREVIEWED_PORTAL_STATUS_HOLD")


def assess_public_synthetic_candidate(candidate: dict) -> dict:
    """Pure safety triage: never authorize publishing or private source tests.

    A field claiming operator review is only a caller assertion, not independent
    proof of content release authorization. Every real asset still needs an
    independent human inspection *before* files are added to the Public repo.
    """
    required = frozenset({
        "kind", "origin", "private_source_included", "private_data_included",
        "credentials_included", "copyright_documents_included",
        "operator_content_review_claimed",
    })
    if not isinstance(candidate, dict) or set(candidate) != required:
        raise ValueError("PUBLIC_CANDIDATE_SCHEMA_HOLD")
    if (candidate["kind"] != "SYNTHETIC_CONTRACT"
            or candidate["origin"] != "INDEPENDENT_PUBLIC_AUTHORING"):
        raise ValueError("PRIVATE_OR_UNREVIEWED_ORIGIN_HOLD")
    for key in (
        "private_source_included", "private_data_included",
        "credentials_included", "copyright_documents_included",
    ):
        if candidate[key] is not False:
            raise ValueError("PUBLIC_PAYLOAD_LEAK_HOLD")
    if candidate["operator_content_review_claimed"] is not True:
        raise ValueError("HUMAN_CONTENT_REVIEW_REQUIRED_HOLD")
    return {
        "scope": "PUBLIC_SYNTHETIC_ONLY",
        "state": "SYNTHETIC_CANDIDATE_ASSERTION_ONLY",
        "public_release_authorized": False,
        "private_agent_javis_source_tested": False,
        "private_agent_javis_brain_source_tested": False,
        "private_pr_merge_gate_passed": False,
        "review_claim_independently_verified": False,
        "network_or_private_repo_requests": 0,
    }
