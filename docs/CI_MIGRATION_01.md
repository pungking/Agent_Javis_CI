# CI-MIGRATION-01 — Public synthetic-only migration pilot (review-only)

This repository is **Public**. The authoritative projects remain **Private**.
This phase adds **original illustrative contracts and fake test fixtures only**.
It does not import, fetch, re-license, mirror, or republish private source or evidence.

## Families assessed and provisional disposition

| Family | Public pilot | Private tests remain authoritative |
|---|---|---|
| Weekly intake readiness / scheduler separation | Synthetic presence, status and denial behavior | Actual task schedule, operator/actor identity and delivery evidence |
| Publisher and single Writer boundaries | Synthetic event denial | Real GitHub workflow definitions, permissions, tokens and run provenance |
| Pending / receipt / readback | Fake SHA-256 equality and new-archive/no-op examples | Actual Markdown, bytes, receipt and remote Git content |
| Later allowed push and recovery | Abstract two-link ancestry flags and recovery denial | Real Git DAG comparisons, commit diffs, Run, Job and readback |
| Mission / policy / Core | Illustrative state and approval DENY checks | Actual mission schemas, policy engine, approval/ledger and full unit tests |
| Legacy and orchestration | Fake no-executor / illegal-transition examples | Original frozen blobs, source parity, routing internals and all legacy regression |

**Not in the Public pilot:** real mission data, private implementation, logs,
original Git IDs or SHA manifests, scheduled execution outcomes, Vault, any
hardware/GPU or Mac verification, paid APIs, environment credentials, private
PDFs, live GitHub workflow access or cross-repository dispatch.

## Exactly what the new tests assert

- All fixtures carry an exact `SYNTHETIC_ONLY` marker; unknown fields are
  rejected, so raw Markdown, credentials or log fields cannot be slipped into
  a test packet under an unexpected key.
- Direct and later-change demo cases are separated. A later-change case
  requires two **synthetically asserted** ancestry flags. Neither flag
  authenticates a real Git comparison.
- Failure, skipped/running state, manual trigger, no-op, absent new receipt,
  mismatched fake SHA and missing readback are all denied.
- Illustrative mission transitions are DENY by default; human approval is a
  fake boolean and **never grants real executor authority**.
- A passed test means only `PUBLIC_SYNTHETIC_* `, not production success,
  original source parity, or verified private repository CI.

## Reproducibility and migration safety gates

1. Keep `.github/workflows/public-ci.yml` unchanged: read-only permissions,
   no secrets, no private checkout, Python 3.11/3.12, test discovery only.
2. Keep strict `tests/test_repository_boundary.py` allowlisting all public
   files. Propose additional files only after independent disclosure review.
3. Validate current Public main SHA, exact Draft PR HEAD and complete diff,
   both Python CI matrix jobs, and existing starter tests.
4. Independently revalidate that source files, workflows and protected
   artifacts in the two Private repositories were **not changed**.
5. Never label public-only tests as private regression/parity. Parity requires
   a separately authorized, isolated verification of original source, exact
   revision mapping, and security review.
6. Keep all private workflows and their existing required checks unchanged
   during this pilot. No schedule/rerun, deployment, cross-repo trigger,
   secrets, paid provider, Mac operation, or rule changes.
7. Public PR merge and any removal of Private CI require separate explicit
   approval and demonstrated gate equivalence.

## Billing and threat-model note

GitHub states that standard GitHub-hosted runners used in public repositories
are free, while private-runner usage draws on plan allowances or billing.
A **reusable workflow called by a Private workflow is billed to the caller**;
simply calling a Public workflow does not move the caller's execution cost.
This pilot runs synthetic tests *within the Public repository* instead.

Official documentation:
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target

Keep `pull_request_target`, cross-repo private checkout, deployment
credentials and untrusted-code-with-secrets out of this Public workflow.

## Exit criteria

The pilot may be considered for acceptance only when the final Draft PR HEAD
passes both Public Python matrix jobs and the strict repository boundary check.
The outcome does **not** supersede Private CI, authorize external actions, or
change any scheduled delivery freeze.


## CI-MIGRATION-02 — Five fictional Brain-stage families (Draft, HOLD)

This Public addition implements **five original synthetic teaching models**:
readiness, routing, packet consistency, run/job/step outcomes, and recovery.
They use only invented labels, Boolean flags and literal fake digests.

- Exactly 16 new unittest methods, with multiple parameterized subtests.
- The original Private Brain 121 candidate methods are NOT imported,
  reimplemented line-by-line, or counted as Public equivalence.
- Consistent synthetic inputs return a **non-operational** result:
  no private-source parity, real Git provenance, actor authentication,
  archive readback, deployment permission or public-release approval.
- Unknown fields, unknown stage names, malformed types, secret/log field
  injection and unsupported status enumerations fail closed.
- No new files; existing Public allowlist, workflows, permissions, runner
  matrix, secrets policy and Private repositories remain unchanged.
- CI acceptance is limited to the final exact Public Draft PR HEAD
  and natural Python 3.11 / 3.12 jobs, never a Private CI PASS.
- Publication approval, merge, Private CI removal, W47, Mac/Obsidian,
  paid providers and actual agent execution remain on HOLD.

## CI-MIGRATION-03 — Synthetic routing separation refinement (HOLD)

The two *fictional* event boundaries are now separate: a publisher configured
manual-only and a single writer keyed to the synthetic main Pending push.
Previously a generic fictional publisher success and push event could be
mistaken for the same execution actor. Disallowed publisher auto-triggers,
wrong writer triggers and malformed trigger labels are now denied.

This remains NON-PARITY: real Brain task recurrence/actor identity, workflow
source strings and permissions, concrete receipts and hashes, Git ancestry,
real Run/Job/Step origin and actual archive readback are not validated here.
Passing Public CI does not authorize Private CI replacement or W47 execution.
