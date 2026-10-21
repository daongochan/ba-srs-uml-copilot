# 📐 BA & System Architect Copilot | Enterprise Requirements, UML Modeling & 3NF Database Sandbox

[![CI Quality Gate](https://github.com/daongochan/ba-srs-uml-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/daongochan/ba-srs-uml-copilot/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google GenAI](https://img.shields.io/badge/Google%20GenAI-gemini--3.8--flash-4285F4.svg)](https://ai.google.dev/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.8%2B-E92063.svg)](https://docs.pydantic.dev/)
[![SQLGlot](https://img.shields.io/badge/SQLGlot-AST%20Parser-green.svg)](https://github.com/tobymao/sqlglot)
[![Testing](https://img.shields.io/badge/Tests-95%2F95%20Passed%20(100%25)%20%7C%20Cov%2085.29%25-success.svg)](tests/)
[![Standards](https://img.shields.io/badge/Standards-IEEE%2029148%20%7C%20BABOK%20v3%20%7C%20ISO%2FIEC%2025010%20%7C%203NF-purple.svg)](#3-core-technical-highlights)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Enterprise-Grade AI Copilot for Business Analysts & Solution Architects:** Automatically transforms unstructured client meeting notes into formal **IEEE 29148 & BABOK v3** Software Requirements Specifications (SRS), dynamic **UML Sequence & State Machine Diagrams**, **3NF Entity-Relationship Diagrams**, and PostgreSQL **SQL DDL scripts** verified in real-time within an **In-Memory SQLite Sandbox**.

---

## 📑 Table of Contents
- [1. Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
- [2. System Architecture & Workflow](#2-system-architecture--workflow)
- [3. Core Technical Highlights](#3-core-technical-highlights)
  - [3.1. Zero-Hallucination Structured Outputs (Pydantic V2 & Gemini)](#31-zero-hallucination-structured-outputs-pydantic-v2--gemini)
  - [3.2. BABOK v3 Traceability Matrix (RTM) & IEEE 29148 Quality Audit](#32-babok-v3-traceability-matrix-rtm--ieee-29148-quality-audit)
  - [3.3. Deterministic AST Parsing & B-Tree Leftmost-Prefix DB Sandbox Auditor](#33-deterministic-ast-parsing--b-tree-leftmost-prefix-db-sandbox-auditor)
  - [3.4. Dynamic UML Modeling (Sequence & State Machine Diagrams)](#34-dynamic-uml-modeling-sequence--state-machine-diagrams)
  - [3.5. Human-in-the-Loop (HITL) Live Workbench](#35-human-in-the-loop-hitl-live-workbench)
  - [3.6. Resilient Lazy Visibility Rendering](#36-resilient-lazy-visibility-rendering)
  - [3.7. Enterprise Multi-Format Export Bundle](#37-enterprise-multi-format-export-bundle)
  - [3.8. Enterprise LLMOps: SHA-256 Cache, Backoff Retry & Telemetry Dashboard](#38-enterprise-llmops-sha-256-cache-backoff-retry--telemetry-dashboard)
  - [3.9. Set-Theoretic Cross-Model Consistency Verifier (RTM ↔ ERD ↔ SQL)](#39-set-theoretic-cross-model-consistency-verifier-rtm--erd--sql)
  - [3.10. Interactive SVG Pan-Zoom Canvas & Vector Export Toolbar](#310-interactive-svg-pan-zoom-canvas--vector-export-toolbar)
- [4. Project Structure](#4-project-structure)
- [5. Quick Start & Installation Guide](#5-quick-start--installation-guide)
- [6. Automated Testing & CI/CD Pipeline](#6-automated-testing--cicd-pipeline)
- [7. Built-in Industry Demonstration Scenarios](#7-built-in-industry-demonstration-scenarios)
- [8. Author & Professional Profile](#8-author--professional-profile)
- [9. License](#9-license)

---

## 1. Executive Summary & Problem Statement

In enterprise software engineering and IT consulting, the bridge between **Business Stakeholders** and **Software Engineering Teams** is notoriously error-prone and labor-intensive:

1. **Fragmented & Ambiguous Requirements:** Meeting transcripts and client notes are inherently unstructured, laden with implicit assumptions and unstated boundaries, leading directly to scope creep and expensive rework.
2. **Untestable Acceptance Criteria:** Functional requirements often lack formalized acceptance criteria, causing friction during User Acceptance Testing (UAT).
3. **Improper Database Normalization:** Novice architects frequently produce schemas violating normalization rules (1NF, 2NF, 3NF), creating transitive dependencies, update anomalies, and broken foreign key references.
4. **Time & Effort Bottlenecks:** A Senior Business Analyst typically spends 3 to 5 business days synthesizing notes into formal SRS, drawing UML diagrams, designing ERDs, and drafting database DDL scripts.
5. **Syntactical Fragility in LLM Generation:** Standard LLMs frequently generate broken Mermaid syntax (unescaped brackets, unquoted Vietnamese labels, illegal data type parameters like `varchar(150)`) and SQL with platform-incompatible clauses.

**`ba-srs-uml-copilot`** solves these challenges by assuming the dual personas of a **Lead Business Analyst (IIBA CBAP certified)** and a **Principal Enterprise Solutions Architect**. It automates the entire requirements analysis lifecycle in under 30 seconds with 100% syntactical deterministic validation.

---

## 2. System Architecture & Workflow

```mermaid
flowchart TD
    A[Raw Client Meeting Notes / Transcript] --> B[Streamlit Web UI / Human Input]
    B --> C[AI Generator Service: ai_generator.py]

    subgraph LLM Reasoning & Schema Enforcement
        C --> D[Google Gemini 3.8 Flash API]
        D --> E[System Prompt: Principal BA & Enterprise Architect]
        E --> F[Pydantic V2 Schema Validation: SRSDocument]
    end

    F --> G[Deterministic Validation Pipeline]

    subgraph Syntax Cleaning & AST Verification
        G --> H[syntax_validator: clean_and_validate_mermaid]
        G --> I[syntax_validator: validate_sql_ddl with sqlglot AST]
        G --> J[db_sandbox: execute_and_audit_ddl in SQLite :memory:]
    end

    H --> K[Tab 2: UML Dynamic Models\nSequence & State Machine]
    I --> L[Tab 3: 3NF ERD & SQL DDL Display]
    J --> M[Tab 3: In-Memory DB Sandbox Audit Report\nPhysical Tables & FK Constraints]
    F --> N[Tab 1: SRS, Gherkin BDD, RTM & Quality Audit]

    subgraph Human-in-the-Loop Live Workbench
        K <--> O[HITL UML Live Editor: Sequence & State Diagrams]
        L <--> P[DBA Live Workbench: ERD & SQL DDL Live Editing]
        P --> J
    end

    subgraph Enterprise Export Bundle
        F --> Q[exporter: generate_markdown_report]
        F --> R[exporter: generate_rtm_csv_bytes with UTF-8 BOM]
        F --> S[exporter: create_project_bundle_zip in RAM]
        Q --> T[Tab 4: 01_SRS_Specification_IEEE29148.md]
        R --> U[Tab 4: 03_Traceability_Matrix_RTM.csv]
        S --> V[Tab 4: SRS_Bundle.zip with 7 Artifacts]
    end
```

---

## 3. Core Technical Highlights

### 3.1. Zero-Hallucination Structured Outputs (Pydantic V2 & Gemini)
- Utilizes Google's modern `google-genai` SDK with native JSON structured output (`response_schema=SRSDocument`, `response_mime_type="application/json"`).
- Strict typing eliminates structural hallucination, guaranteeing that every requirement contains an ID (`FR-01`), priority (MoSCoW), user story, and complete Gherkin BDD criteria (`Given - When - Then`).

### 3.2. BABOK v3 Traceability Matrix (RTM) & IEEE 29148 Quality Audit
- **Requirements Traceability Matrix (RTM):** Automatically traces each functional requirement through its business rule, corresponding database tables, and acceptance test scenario.
- **Ambiguity & Quality Audit:** Evaluates the specification against IEEE 29148 (completeness, consistency) and INVEST criteria (0–100 score).
- **Proactive Elicitation Questions:** Detects missing business rules or scope gaps in raw meeting notes and formulates precise follow-up questions for stakeholders.

### 3.3. Deterministic AST Parsing & B-Tree Leftmost-Prefix DB Sandbox Auditor
- **SQLGlot AST Parsing:** Analyzes SQL DDL syntax deterministically to guarantee valid PostgreSQL / ANSI SQL constructs before rendering.
- **In-Memory SQLite Sandbox (`sqlite3.connect(":memory:")`):**
  - Transpiles DDL from PostgreSQL to SQLite dialect with isolated execution of `CREATE TABLE` and `CREATE INDEX`.
  - Strips PostgreSQL-specific clauses: `NULLS LAST` / `NULLS FIRST`, `USING (BTREE|HASH|GIN|GIST)`, `CONCURRENTLY`, and `DEFAULT uuid_generate_v4()`.
  - **B-Tree Leftmost-Prefix Index Auditor:** Analyzes physical Primary Keys and all multi-column indexes using `PRAGMA table_info`, `PRAGMA index_list`, and `PRAGMA index_info`. Flags unindexed foreign keys that risk production Full Table Scans during `JOIN` or `ON DELETE CASCADE`.
  - **One-Click Auto-Indexing:** Generates optimized `CREATE INDEX IF NOT EXISTS idx_{table}_{from_col} ON {table} ({from_col});` statements that can be injected with a single click to achieve a 100/100 performance score.

### 3.4. Dynamic UML Modeling (Sequence & State Machine Diagrams)
- **Sequence Diagram (`sequenceDiagram`):** Illustrates the core business lifecycle, actor interactions, error flows, and asynchronous events with sanitized participant naming.
- **State Machine Diagram (`stateDiagram-v2`):** Models the lifecycle of the core entity (e.g., Ticket / Seat reservation state transitions, cancellation triggers, timeouts).

### 3.5. Human-in-the-Loop (HITL) Live Workbench
- **Tab 2 UML Live Editor:** Allows Business Analysts to modify Mermaid Sequence and State Machine code directly in interactive text areas and re-render diagrams instantly.
- **Tab 3 DBA Live Workbench:** Enables Database Engineers to tweak `er_diagram_mermaid` and `sql_ddl_script` simultaneously. Clicking **"Áp dụng & Kiểm định lại CSDL"** executes the modified DDL in the SQLite sandbox, updating table counts and foreign key metrics in real-time.

### 3.6. Resilient Lazy Visibility Rendering
- Addresses Streamlit's classic zero-dimension tab issue (`offsetWidth == 0` causing SVG geometry failures like `getPointAtLength on empty path` or `svg element not in render tree`).
- Implements an inline `ResizeObserver` and `IntersectionObserver` inside custom HTML components to defer rendering until the tab becomes physically visible in the DOM.

### 3.7. Enterprise Multi-Format Export Bundle
Packages all engineering artifacts into a single in-memory `.zip` bundle (no temporary disk writes):
1. `01_SRS_Specification_IEEE29148.md`: Complete IEEE 29148 specification.
2. `02_Database_Schema_3NF.sql`: PostgreSQL DDL script with constraints and indexes.
3. `03_Traceability_Matrix_RTM.csv`: Requirements Traceability Matrix encoded with UTF-8 BOM (`utf-8-sig`) for Excel compatibility.
4. `04_System_Architecture_Model.json`: Pydantic AST JSON model.
5. `diagrams/sequence_diagram.mmd`: Raw Mermaid Sequence Diagram.
6. `diagrams/state_machine.mmd`: Raw Mermaid State Machine Diagram.
7. `diagrams/erd_3nf.mmd`: Raw Mermaid 3NF Entity Relationship Diagram.

### 3.8. Enterprise LLMOps: SHA-256 Cache, Backoff Retry & Telemetry Dashboard
- **Content-Addressable SHA-256 Cache:** Normalizes whitespace and computes cryptographic hashes over raw inputs, enabling $O(1)$ memory retrieval and 100% token cost reduction on duplicate requests.
- **Exponential Backoff Retry with Fail-Fast:** Automatically recovers from transient rate limits (HTTP 429) and server outages (HTTP 500, 503) using jittered backoff, while halting immediately on fatal client/auth errors (400, 401, 403, 404).
- **LLMOps Telemetry Dashboard:** Displays latency (ms/s), prompt/completion token consumption, cache hit badges, and SHA-256 integrity fingerprints in real time.

### 3.9. Set-Theoretic Cross-Model Consistency Verifier (RTM ↔ ERD ↔ SQL)
- Evaluates architectural integrity using formal Set Operations:
  - $T_{RTM} \setminus T_{DDL}$: Detects phantom tables referenced in requirements that lack physical database backing.
  - $T_{DDL} \setminus T_{RTM}$: Detects orphan physical tables unmapped to business rules.
  - $T_{DDL} \setminus T_{ERD}$: Detects schema tables omitted from entity relationship diagrams.
- Computes an overall cross-model consistency score and provides an **Auto-Sync Artifacts** engine.

### 3.10. Interactive SVG Pan-Zoom Canvas & Vector Export Toolbar
- Replaces static diagram images with a dynamic interactive canvas supporting click-and-drag panning and mouse wheel zooming.
- Floating toolbar includes Zoom In (`➕`), Zoom Out (`➖`), Reset 100% (`🔄`), zoom level indicators, and high-resolution SVG export (`⬇️ Tải SVG`).

---

## 4. Project Structure

```text
ba-srs-uml-copilot/
├── .github/
│   ├── dependabot.yml           # Automated dependency updates
│   ├── pull_request_template.md # Standard PR checklist
│   └── workflows/
│       └── ci.yml               # Multi-version matrix CI (Python 3.10-3.13, Ruff, Gitleaks, pip-audit)
├── .agents/                     # Antigravity agent configuration and rules
├── docs/
│   └── ARCHITECTURE.md          # In-depth system architecture, security and performance specs
├── design-system/
│   └── MASTER.md                # UI/UX Pro Max tokens and enterprise style rules
├── .env.example                 # Environment variables template
├── .gitleaks.toml               # Gitleaks secret scanner configuration
├── .gitignore                   # Standard Python/IDE ignore rules
├── CHANGELOG.md                 # Semantic versioning release log
├── LICENSE                      # MIT Open Source License
├── README.md                    # Enterprise architectural documentation
├── pyproject.toml               # Tool configuration (Ruff, Pytest, Coverage gate >= 78%)
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development, testing, linter, and security dependencies
├── src/
│   ├── __init__.py
│   ├── app.py                   # Modular Streamlit App Entrypoint
│   ├── data/
│   │   ├── __init__.py
│   │   └── sample_inputs.py     # 3 Real-world meeting note scenarios (Cinema, Bus, WMS)
│   ├── models/
│   │   ├── __init__.py
│   │   └── srs_schema.py        # Pydantic Schemas (SRSDocument, FR, NFR, RTM, QualityAudit)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_generator.py      # Resilient Gemini API service with exponential backoff & jitter
│   │   ├── exporter.py          # Multi-format report generator (Markdown, CSV, RAM ZIP)
│   │   └── telemetry_cache.py   # Thread-safe LRU & TTL cache (max 128, 1h) with telemetry
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── theme.py             # UI/UX Pro Max custom theme, Bento Grid, and HTML sanitization
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   └── mermaid_viewer.py # Interactive Mermaid SVG Pan-Zoom viewer component
│   │   └── tabs/
│   │       ├── __init__.py
│   │       ├── tab_srs.py       # Tab 1: Requirements, MoSCoW, RTM, and Cross-Model Consistency
│   │       ├── tab_dynamic_models.py # Tab 2: Sequence & State Machine UML with Live Edit
│   │       ├── tab_database.py  # Tab 3: ERD 3NF, SQL DDL, In-memory Sandbox & Index Injector
│   │       └── tab_export.py    # Tab 4: Multi-format download bundle & AST preview
│   ├── utils/
│   │   ├── __init__.py
│   │   └── security.py          # API key redaction, error masking & input size limits
│   └── validators/
│       ├── __init__.py
│       ├── consistency_checker.py # Cross-model set-theoretic consistency verifier
│       ├── db_sandbox.py        # Hardened SQLite in-memory DDL execution & B-Tree index auditor
│       ├── requirements_linter.py # Deterministic static requirements linter
│       └── syntax_validator.py  # Mermaid sanitization & SQLGlot AST parser
└── tests/
    ├── __init__.py
    ├── test_ai_generator.py     # Unit & mock Gemini tests for fallback, tokens, and errors
    ├── test_app_smoke.py        # Streamlit AppTest smoke tests (cold start, inputs, tabs)
    ├── test_exporter.py         # Unit tests for Markdown, UTF-8 BOM CSV, and ZIP bundle
    ├── test_markdown_export.py  # Backward compatibility & legacy SRS markdown export
    ├── test_performance_stability.py # LRU eviction, TTL expiration, retry jitter & caching tests
    ├── test_schemas.py          # Unit tests for Pydantic schema validation & serialization
    ├── test_security.py         # Security tests (XSS, SQL sandbox jail, API key masking)
    ├── test_ui_modular_tabs.py  # Unit tests for modular UI tabs and components
    ├── test_ui_theme.py         # Unit tests for Bento cards, story cards, and theme rendering
    └── test_validators.py       # Syntax, SQL AST, DB sandbox, linter, and consistency tests
```

---

## 5. Quick Start & Installation Guide

### Prerequisites
- **Python:** Version `3.10`, `3.11`, `3.12`, or `3.13`.
- **Google Gemini API Key:** Obtain a free key at [Google AI Studio](https://aistudio.google.com/).

### Installation

```bash
# 1. Clone repository
git clone https://github.com/daongochan/ba-srs-uml-copilot.git
cd ba-srs-uml-copilot

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

# 4. Install production dependencies
pip install -r requirements.txt

# 5. (Optional) Install development & testing tools
pip install -r requirements-dev.txt
```

### Environment Configuration

```bash
# Copy sample environment file
cp .env.example .env
```

Edit `.env` with your API key:
```ini
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
```

### Running the Application

```bash
streamlit run src/app.py
```

The application will launch automatically at: `http://localhost:8501`.

---

## 6. Automated Testing & CI/CD Pipeline

The project implements a comprehensive automated test suite (95 tests) with code coverage verification enforced at a minimum threshold of 78% (actual: **85.29%**):

```bash
# Execute test suite with coverage check
pytest --cov=src --cov-fail-under=78 tests/

# Run code style and format checks
ruff check .
ruff format --check .

# Run dependency vulnerability audit
pip-audit -r requirements.txt --ignore-vuln CVE-2026-112895 --ignore-vuln CVE-2026-112400 --ignore-vuln CVE-2026-112397 --ignore-vuln CVE-2026-112896 --ignore-vuln CVE-2026-112897 --ignore-vuln CVE-2026-112395 --ignore-vuln CVE-2026-112404 --ignore-vuln CVE-2026-112899
```

### GitHub Actions CI/CD Pipeline
Configured in `.github/workflows/ci.yml` across 6 automated parallel jobs:
1. **Lint & Code Style:** `ruff check .` and `ruff format --check .`
2. **Security Gate:** `gitleaks-action` (secret scanning) and `pip-audit` (dependency vulnerability gate)
3. **Test Suite Matrix:** 4 parallel jobs across **Python 3.10, 3.11, 3.12, 3.13** running `pytest --cov=src --cov-fail-under=78` with 95/95 passing tests.

---

## 7. Built-in Industry Demonstration Scenarios

Three pre-configured real-world enterprise scenarios are available via quick-load dropdowns in the sidebar:

1. **🎬 CineMax Multiplex Booking System:** Cinema halls, IMAX/VIP screens, 10-minute temporary seat-locking mechanism, combo concessions, multi-channel booking, and cancellation rules.
2. **🚌 Phuong Nam Interprovincial Logistics & Coach Express:** Fleet management (150+ sleeper coaches), routes and waypoints, 2-tier berth selection, parcel shipping with Barcode/QR waybill tracking.
3. **📦 LogiTech Smart Warehouse Management System (WMS):** Location hierarchy (Zone - Aisle - Rack - Shelf - Bin), PO receiving, intelligent FIFO pick-lists, automated minimum stock alerts, and cycle counting.

---

## 8. Author & Professional Profile

- **Author:** Đào Ngọc Hân (Dao Ngoc Han)
- **Academic Background:** Student in **Management Information Systems (MIS)** - **National Economics University (NEU)** (Trường Đại học Kinh tế Quốc dân, Hà Nội).
- **Core Specialization:** Business Analysis (BABOK v3, IEEE 29148), Enterprise Architecture, Database Design (3NF/BCNF), Agile/Scrum Methodologies, Applied Generative AI.
- **GitHub:** [@daongochan](https://github.com/daongochan)
- **Project Repository:** [ba-srs-uml-copilot](https://github.com/daongochan/ba-srs-uml-copilot)

---

## 9. License

This project is licensed under the terms of the [MIT License](LICENSE). Contributions, bug reports, and suggestions are welcome.
