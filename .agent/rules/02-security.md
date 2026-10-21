# Security & Compliance Rules

## 1. Zero-Secrets Policy
- **No Hardcoded Credentials**: Never write API keys, Personal Access Tokens (PAT), passwords, private keys, or webhook URLs in any code, config file, documentation, or commit message.
- **Environment Isolation**:
  - All sensitive tokens must reside exclusively in `.env` (local) or GitHub Secrets (CI).
  - The `.env` file MUST always be excluded in `.gitignore`.
  - Maintain `.env.example` with sanitized placeholders (`YOUR_GEMINI_API_KEY_HERE`, `YOUR_GITHUB_PAT_HERE`).
- **Telemetry Sanitization**: Telemetry metrics and error messages must never expose raw API keys or user credentials. SHA-256 hashes must be computed only over normalized inputs.

## 2. Input Validation & AST Sanitization
- **Strict Data Contracts**: All AI generator inputs and outputs must pass through Pydantic v2 schemas (`SRSDocument`, `QualityAudit`, `TraceabilityItem`).
- **SQL DDL Security**:
  - Always validate SQL scripts using `sqlglot` AST parsing before sandbox execution.
  - Reject dangerous dialect statements and arbitrary OS commands.
  - Isolate SQLite execution strictly to temporary in-memory instances (`:memory:`). Never write unverified DDL to persistent physical disks.
- **Mermaid Diagram Safety**: Sanitize and strip markdown code fences and control characters to prevent UI injection attacks in interactive SVG canvas.

## 3. Dependency & Supply Chain Security
- Pin minimum versions for all critical libraries in `requirements.txt`.
- Never install unverified packages from untrusted third-party indices.
- Run Dependabot scans weekly to remediate vulnerable dependencies.

## 4. Git Security & Pre-Commit Protection
- Run secret scanning patterns (`gitleaks` / regex scanner) before every commit.
- Never bypass branch protection or secret detection rules.
- If a secret is ever accidentally committed, rotate and revoke the credential immediately; do not rely merely on a subsequent commit to hide it.
