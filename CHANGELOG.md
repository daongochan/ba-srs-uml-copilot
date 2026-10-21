# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-10-21

### Added
- **Safety-Net Testing Infrastructure (Lô A)**:
  - Streamlit `AppTest` smoke test suite covering cold-starts, scenario loading, missing API key handling, and multi-tab rendering.
  - Comprehensive Mock Gemini API tests for token fallbacks, transient network retries, and syntax resilience.
  - Enforced test coverage threshold gate (`--cov-fail-under=78`), increasing repository coverage to **85.29%** across 95 tests.
  - Security gates in CI: automated Gitleaks secret scanning and pip-audit vulnerability checks.

- **Security Hardening (Lô B)**:
  - Mermaid strict security level (`securityLevel: 'strict'`) and HTML/SVG script tag sanitization.
  - XSS defense across all custom UI components via `html.escape` in `src/ui/theme.py`.
  - Hardened In-Memory SQLite Sandbox in `src/validators/db_sandbox.py` blocking `ATTACH DATABASE`, `DETACH`, `VACUUM INTO`, and `load_extension`.
  - Sandbox resource exhaustion defenses: 64KB DDL script size limit, 50 statement execution limit, and 100,000 opcode progress handler timeout.
  - Sensitive credential protection in `src/utils/security.py`: automatic masking of API keys and redaction from error messages and logs.
  - Meeting notes input bounding: 50,000 character maximum enforced at both frontend UI and backend services.

- **Performance & Stability Enhancements (Lô C)**:
  - Thread-safe `DeterministicSRSCache` in `src/services/telemetry_cache.py` with `collections.OrderedDict` LRU eviction (`max_size=128`) and TTL expiration (`ttl_seconds=3600.0`).
  - Pre-compiled module-level regular expressions across syntax validators, database sandbox, and consistency checkers.
  - AST DDL memoization using `@functools.lru_cache(maxsize=256)`.
  - Memory optimization: eliminated redundant double deepcopy passes on cache hits and writes.
  - Resilient exponential backoff with full random jitter (`random.uniform(0, delay)`) to prevent API thundering herd.

- **Modular UI Architecture & Formatting (Lô D)**:
  - Modularized `src/app.py` (reduced from 1,152 lines down to 240 lines):
    - `src/ui/components/mermaid_viewer.py`: Interactive Mermaid SVG canvas with pan, zoom, reset, and SVG download.
    - `src/ui/tabs/tab_srs.py`: Tab 1 - SRS specifications, Bento KPI metrics, MoSCoW cards, and RTM table.
    - `src/ui/tabs/tab_dynamic_models.py`: Tab 2 - Sequence and State Machine UML diagrams with live editing.
    - `src/ui/tabs/tab_database.py`: Tab 3 - 3NF ERD, SQL DDL, SQLite RAM Sandbox audit, and auto-indexing.
    - `src/ui/tabs/tab_export.py`: Tab 4 - Multi-format project bundle exporter and AST preview.
  - Codebase-wide standardization via `ruff format` (42/42 files cleanly formatted).
  - Explicit type annotations added to internal generation handlers (`_call_gemini() -> Any`).

- **Documentation & Architecture Synchronization (Lô E)**:
  - Synchronized `README.md` with updated metrics (95/95 tests passing, 85.29% coverage), detailed directory tree, and developer setup instructions.
  - Comprehensive architectural specification in `docs/ARCHITECTURE.md` covering threat modeling, security mitigations, caching strategies, and industrial standard mappings.

## [1.1.0] - 2026-10-21

### Added
- **UI/UX Pro Max Design System**: Integrated design tokens based on `design-system/MASTER.md`.
- **Top Navigation Banner**: Added brand header with system badges (`IEEE 29148:2018`, `BABOK v3`, `3NF Sandbox`) and a 4-step workflow stepper.
- **Smart Expander**: Dynamic collapsing meeting notes input area maximizing workbench workspace.
- **Bento KPI Dashboard**: Custom HTML/CSS equal-height metric cards with dynamic progress bars on Tab 1 and Tab 3.
- **MoSCoW User Story Cards**: Redesigned functional requirement cards with color-coded priority badges and structured Gherkin BDD blocks (`Given`/`When`/`Then`).
- **LLMOps Telemetry Widget**: Sidebar panel displaying real-time latency, token usage split, and SHA-256 fingerprint.

## [1.0.0] - 2026-10-21

### Added
- **Core AI SRS Generator**: Structured JSON schema output adhering to IEEE 29148 and BABOK v3.
- **Dynamic UML Modeling**: Sequence Diagram and State Machine Diagram rendered via interactive SVG Pan-Zoom canvas.
- **3NF Relational Architecture**: ERD Mermaid diagram and PostgreSQL/ANSI SQL DDL generator.
- **In-Memory SQLite Sandbox**: Physical database audit in RAM with automated B-Tree index health scoring and auto-healing.
- **Cross-Artifact Consistency Verifier**: Set-algebraic consistency verification across RTM, ERD, and SQL DDL tables.
- **Enterprise Export Bundle**: Automated generation of complete zip deliverables (Markdown, SQL, CSV, JSON, Mermaid).
- **Content-Addressable Cache**: SHA-256 caching layer with exponential backoff and jitter.
