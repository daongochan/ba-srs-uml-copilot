# /fix-ci — Automated CI Diagnosis & Remediation Workflow

This workflow diagnoses failed GitHub Actions CI runs, identifies the root cause, verifies fixes locally, and triggers `/ship` to restore green build status.

## Trigger
- User invokes `/fix-ci` or a GitHub Actions run fails on a pull request or branch.

---

## Step 1: Fetch CI Failure Logs
1. Use GitHub MCP tools (`get_workflow_run_logs` / `list_workflow_runs`) or GitHub CLI to inspect the latest failed workflow run.
2. Locate the specific failing step (e.g. `Ruff Linter`, `Pytest Suite`, `Dependency Installation`).
3. Extract the exact stack trace, failing test assertion, or linting violation.

---

## Step 2: Root Cause Analysis
1. Categorize the failure:
   - **Linting violation**: Unformatted code, unused imports, line-length, syntax.
   - **Test regression**: Broken assertion, missing mock data, schema mismatch.
   - **Environment / Dependency issue**: Missing package in `requirements.txt` or Python version discrepancy.
   - **Syntax / AST error**: Malformed YAML in `.github/workflows/` or broken SQL parsing.
2. Formulate a targeted fix addressing the root cause without modifying core application behavior unless bugged.

---

## Step 3: Local Reproduction & Verification
1. Reproduce the exact CI failure locally:
   - For lint failure:
     ```powershell
     .\.venv\Scripts\python.exe -m ruff check .
     ```
   - For test failure:
     ```powershell
     .\.venv\Scripts\python.exe -m pytest <path_to_failing_test> -v
     ```
2. Apply the fix.
3. Run the full local test suite to prevent collateral regressions:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest -v
   ```

---

## Step 4: Re-ship & Verify
1. Invoke the `/ship` workflow:
   - Stage the fix.
   - Commit with message: `fix(ci): <explanation of failure and resolution>`.
   - Push to current branch to trigger a fresh GitHub Actions run.
2. Monitor workflow progress until GitHub Actions CI displays green status.
