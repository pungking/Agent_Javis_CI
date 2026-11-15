# Agent_Javis_CI — public synthetic CI starter

This Public repository is a **test-only** sandbox for synthetic R&D discovery data contracts. It is **not a mirror**, does **not pull private repositories**, and cannot establish that private Javis code passes the same tests. The `Agent_Javis` and `Agent_Javis_Brain` repositories must remain Private.

## First official smoke test

1. Review every file. Run `python3 -B -m unittest discover -s tests -p 'test_*.py' -v` locally.
2. Use `bash scripts/publish_public_repo.sh` only after independently authorizing publication and verifying the GitHub account. This creates **only** `pungking/Agent_Javis_CI` as Public. It will never change visibility of existing repositories.
3. In GitHub open **Agent_Javis_CI > Actions > Public synthetic CI only**. Verify natural push-triggered Actions on Python 3.11 and 3.12, both `PUBLIC_SYNTHETIC_CI_PASS`.
4. Keep initial public output free of uploads, cached private data, and tokens. Review GitHub terms and repository Actions settings before adding any live data or code.

## Tested contract

Search IRIS, SMTECH and SROME **independently**. A relevant notice found on one portal is a discovery candidate. Group exact official IDs only for optional deduplication; a discovery candidate is not application eligibility, copyright, rights or submission approval.

## Not in scope

GitHub Actions of a *calling private* repository are billed under the private repository. Running a public workflow does not automatically test a private repository's entire source. Implementing cross-repository private source access requires a separate security and permitted-use review.
