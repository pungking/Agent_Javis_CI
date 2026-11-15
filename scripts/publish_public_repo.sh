#!/usr/bin/env bash
# Owner-operated only: creates a NEW public repository containing ONLY this exact manifest.
set -euo pipefail
umask 077

REPO="pungking/Agent_Javis_CI"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"

echo "===== 1. OWNER-GATED PUBLIC PUBLISH PREFLIGHT ====="
command -v gh >/dev/null || { echo GH_CLI_MISSING_HOLD; exit 70; }
command -v git >/dev/null || { echo GIT_MISSING_HOLD; exit 70; }
gh auth status >/dev/null 2>&1 || { echo GH_AUTH_HOLD; exit 70; }
[ ! -e .git ] || { echo EXISTING_GIT_REPO_HOLD; exit 70; }

python3 -B -m unittest discover -s tests -p 'test_*.py' -q

expected_owner="$(gh api user --jq '.login')"
[ "$expected_owner" = "pungking" ] || { echo WRONG_GITHUB_OWNER_HOLD; exit 70; }
if gh repo view "$REPO" >/dev/null 2>&1; then
  echo TARGET_REPOSITORY_ALREADY_EXISTS_HOLD
  exit 70
fi

[ -n "$(git config user.name || true)" ] || { echo GIT_AUTHOR_MISSING_HOLD; exit 70; }
[ -n "$(git config user.email || true)" ] || { echo GIT_EMAIL_MISSING_HOLD; exit 70; }

echo "===== 2. PUBLICATION FILE ALLOWLIST ====="
files=(
  .github/workflows/public-ci.yml
  .gitignore
  README.md
  docs/SECURITY_BOUNDARY.md
  javis_public_ci/__init__.py
  javis_public_ci/contracts.py
  scripts/publish_public_repo.sh
  tests/test_contracts.py
  tests/test_repository_boundary.py
)
for f in "${files[@]}"; do
  [ -f "$f" ] && [ ! -L "$f" ] || { echo "FILE_MISSING_OR_SYMLINK_HOLD=$f"; exit 70; }
done

echo "===== 3. CREATE ONLY NEW PUBLIC CI REPOSITORY ====="
# New independent history; NO git remote or code inherited from either private repo.
git init -q -b main
for f in "${files[@]}"; do git add -- "$f"; done
[ "$(git diff --cached --name-only | wc -l | tr -d ' ')" = "${#files[@]}" ] || {
  echo STAGED_CONTENT_HOLD; exit 70;
}
git commit -q -m "Initial public synthetic-only CI boundary and smoke tests"

gh repo create "$REPO" \
  --public --source=. --remote=origin --push \
  --description "Public synthetic contract CI for Agent_Javis (no private code/data)"

gh repo view "$REPO" --json visibility,url --jq '{visibility: .visibility, url: .url}'
echo "PUBLIC_CI_REPO_CREATED_VERIFY_ACTIONS_RESULTS"
