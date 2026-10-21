# /ship — Automated Verification, Commit & Ship Workflow

This workflow automates pre-flight verification, secret scanning, testing, linting, committing according to Conventional Commits, and pushing changes to GitHub.

## Trigger
- User invokes `/ship` or asks to commit, push, or ship completed changes.

---

## Step 1: Working Tree & Secret Pre-Check
1. Check repository status and changes:
   ```powershell
   git status
   git diff --stat
   ```
2. Ensure no unintended or untracked sensitive files exist (`.env`, `*.pem`, `*.key`, `*.sqlite`, credentials).
3. Scan for hardcoded secret patterns:
   ```powershell
   git diff -U0 | Select-String -Pattern "(?i)(api[_-]?key|secret|token|password|bearer|authorization)\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]"
   ```
   If any potential secret is matched, **STOP IMMEDIATELY**. Do not proceed to commit.

---

## Step 2: Quality Gates (Lint & Test Suite)
1. Run linter and formatting checks:
   ```powershell
   .\.venv\Scripts\python.exe -m ruff check .
   ```
   If linter detects fixable issues, format and fix:
   ```powershell
   .\.venv\Scripts\python.exe -m ruff format .
   ```
2. Run full pytest suite:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest -v --tb=short
   ```
   **Hard stop condition**: If any test fails, STOP and report the error. Never ship broken tests.

---

## Step 3: Documentation Updates
- If features, schemas, or behaviors were modified, update:
  - `CHANGELOG.md` under `[Unreleased]` with Conventional Commit categorization.
  - `README.md` if user-facing instructions changed.

---

## Step 4: Atomic Commit & Push
1. Check the current branch:
   ```powershell
   git branch --show-current
   ```
   - If on `main` and committing a feature or fix, create and switch to a descriptive branch (`feat/<name>` or `fix/<name>`).
2. Stage modified files:
   ```powershell
   git add <modified_files>
   ```
3. Commit with a Conventional Commit message:
   ```powershell
   git commit -m "<type>(<scope>): <concise why-focused description>"
   ```
4. Push to remote origin:
   ```powershell
   git push -u origin <current-branch>
   ```

---

## Step 5: Pull Request & Report
1. If the current branch is not `main`, use GitHub MCP (or GitHub CLI `gh pr create`) to open a Pull Request against `main`.
2. Do **NOT** self-merge into `main`.
3. Provide a final summary to the user:
   - **Branch**: `<branch-name>`
   - **Commit SHA**: `<short-sha>`
   - **PR Status / Link**: URL to review
   - **Test Results**: Total passed tests
