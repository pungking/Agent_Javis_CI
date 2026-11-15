"""Fail if unexpected files are introduced into the public CI starter repo."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = frozenset({
    ".github/workflows/public-ci.yml", ".gitignore", "README.md",
    "docs/SECURITY_BOUNDARY.md", "javis_public_ci/__init__.py",
    "javis_public_ci/contracts.py", "scripts/publish_public_repo.sh",
    "tests/test_contracts.py", "tests/test_repository_boundary.py",
    "docs/CI_MIGRATION_01.md", "javis_public_ci/evidence.py",
    "javis_public_ci/synthetic_gates.py", "tests/test_evidence.py",
    "tests/test_synthetic_gates.py",
})


class PublicationBoundary(unittest.TestCase):
    def test_01_exact_allowlist(self):
        found = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
                 if p.is_file() and ".git" not in p.relative_to(ROOT).parts
                 and "__pycache__" not in p.relative_to(ROOT).parts}
        self.assertEqual(found, ALLOWLIST)

    def test_02_no_sensitive_content_names(self):
        for name in ALLOWLIST:
            self.assertNotIn(".env", name)
            self.assertNotIn(".pem", name)
            self.assertNotIn(".p12", name)
            self.assertNotIn(".sqlite", name)

    def test_03_no_private_repo_read_token_config(self):
        workflow = (ROOT / ".github/workflows/public-ci.yml").read_text()
        self.assertIn("contents: read", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertNotIn("repository_dispatch:", workflow)
        self.assertNotIn("workflow_run:", workflow)
        self.assertNotIn("self-hosted", workflow)


if __name__ == "__main__":
    unittest.main()
