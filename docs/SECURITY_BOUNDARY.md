# Public CI trust boundary

**Purpose:** exercise *public* synthetic contracts using GitHub-hosted runner resources, without deploying any GitHub runner on Agent_Javis-01.

- Private source of truth remains `pungking/Agent_Javis` and `pungking/Agent_Javis_Brain`.
- This repository intentionally does not contain private source, historical commits, Vault, official R&D PDFs, operational evidence, logs, model files, account details, keys, access tokens, or private CI artifacts.
- Public workflow has no repository read credentials beyond its automatic minimal `contents: read` GitHub token, no private checkout, no third-party private code dependencies, no write access, and no external provider calls.
- Public-source unit test success is NOT a substitute for running actual private source regression suites. Do not claim the private repositories' PR checks passed because this public repository passed.
- Actual full private-source CI needs a separately reviewed confidential execution service, or a deliberately released/testable subset of code with its own verified origin and no secrets. Do not bypass repository billing by blindly copying protected source into public logs, artifacts or caches.
- Later integration requires explicit security and source-use review, CI parity tests, revision hash and provenance readback, and owner authorization.
- Agent_Javis-01 is reserved for equipment/GPU/runtime/production-admission tests. Its old KVM-based runner proposal is optional and remains unimplemented.
