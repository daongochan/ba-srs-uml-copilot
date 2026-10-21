# System Architecture & Technical Specifications

## 1. High-Level Architecture Overview

The **BA & System Architect Copilot** transforms raw stakeholder elicitation notes into formal software engineering specifications adhering to international standards (**IEEE 29148:2018**, **BABOK v3**, and **Boyce-Codd / 3NF** database normalization).

```mermaid
graph TD
    A["Raw Meeting Notes<br/>(Stakeholder Elicitation)"] -->|Security Guard: Max 50,000 chars| B["LLMOps Gateway & Cache<br/>(Thread-Safe SHA-256 LRU & TTL Cache)"]
    B -->|Cache Hit O(1)| G["SRSDocument AST"]
    B -->|Cache Miss| C["Gemini AI Principal Engine<br/>(gemini-3.8-flash + Exponential Backoff & Jitter)"]
    C -->|Structured JSON Output| G

    subgraph "Deterministic Verification Engine (RAM Sandbox)"
        G --> D1["Deterministic Linter<br/>(Rule-based IEEE & INVEST)"]
        G --> D2["In-Memory SQLite Sandbox<br/>(Hardened DDL Execution & B-Tree Index Coverage)"]
        G --> D3["Cross-Model Consistency<br/>(Set Algebra: RTM ↔ ERD ↔ SQL)"]
        G --> D4["Syntax & Mermaid Validator<br/>(Pre-compiled Regex & Strict Sanitization)"]
    end

    subgraph "Presentation & Workbench (Modular Streamlit + UI/UX Pro Max)"
        D1 & D2 & D3 & D4 --> H["Enterprise Workbench UI<br/>(Bento KPI Grid & MoSCoW Story Cards)"]
        H --> E["Enterprise Export Bundle<br/>(ZIP, Markdown, SQL DDL, CSV RTM, JSON)"]
    end
```

---

## 2. Core Architectural Components

### A. Elicitation & LLMOps Telemetry Layer (`src/services/`)
- **Content-Addressable Cache (`telemetry_cache.py`)**: Computes a normalized SHA-256 digest of input notes and model parameters. Utilizes a thread-safe `collections.OrderedDict` LRU eviction strategy (`max_size=128`) with TTL expiration (`ttl_seconds=3600.0`). Achieves sub-millisecond retrieval and 100% token cost reduction on repeated runs.
- **Resilient AI Pipeline (`ai_generator.py`)**: Interfaces with the `google-genai` SDK using full jitter exponential backoff (`random.uniform(0, delay)`) to prevent *thundering herd* issues during transient rate limits (HTTP 429 / `RESOURCE_EXHAUSTED`). Enforces strict Pydantic JSON Schema decoding.

### B. Deterministic Verification & Sandbox Layer (`src/validators/`)
- **Requirements Static Linter (`requirements_linter.py`)**: Evaluates requirements without AI hallucination. Flags subjective buzzwords ("dễ dùng", "nhanh chóng", "tối ưu") and verifies SLA quantification against IEEE 29148.
- **In-Memory SQLite Sandbox (`db_sandbox.py`)**: Executes DDL in RAM (`:memory:`) to verify primary keys, foreign key constraints, and enforce Leftmost Prefix B-Tree index coverage. Provides auto-injection of missing indexes.
- **Cross-Model Consistency Verifier (`consistency_checker.py`)**: Uses set algebra to prove equivalence across 3 disparate models:
  $$\Delta = (T_{RTM} \cup T_{ERD} \cup T_{DDL}) \setminus (T_{RTM} \cap T_{ERD} \cap T_{DDL})$$
  Ensures $100\%$ alignment across business requirements, logical entity relations, and physical DDL tables.

### C. Enterprise Presentation & Modular UI Layer (`src/ui/`)
- **Modular Tab Architecture (`src/ui/tabs/`)**:
  - `tab_srs.py`: Requirements specification, Bento KPI metrics, MoSCoW cards, RTM table, and cross-model consistency.
  - `tab_dynamic_models.py`: Sequence and State Machine diagrams with interactive live-editing.
  - `tab_database.py`: ERD 3NF viewer, SQL DDL validation, In-Memory DB Sandbox audit, and one-click index injector.
  - `tab_export.py`: Multi-format enterprise bundle packager and AST JSON preview.
- **Interactive SVG Canvas (`src/ui/components/mermaid_viewer.py`)**:
  - Renders interactive Mermaid diagrams with Pan, Zoom, Reset, and SVG export capabilities.
  - Employs `ResizeObserver` and `IntersectionObserver` for lazy visibility rendering to prevent DOM layout collisions in hidden tabs.

### D. Enterprise Exporter (`src/services/exporter.py`)
- Packages complete deliverables into a timestamped `.zip` bundle comprising:
  1. `01_SRS_<slug>.md`: IEEE 29148 formatted markdown specification.
  2. `02_Schema_<slug>.sql`: 3NF compliant PostgreSQL / ANSI DDL script.
  3. `03_RTM_<slug>.csv`: Requirements Traceability Matrix formatted for Excel (`utf-8-sig`).
  4. `04_Model_<slug>.json`: Complete Pydantic AST JSON document.
  5. `05_Sequence_<slug>.mmd`, `06_State_<slug>.mmd`, `07_ERD_<slug>.mmd`: Mermaid diagram sources.

---

## 3. Security Hardening Architecture

| Threat Vector | Mitigation Strategy | Implementation |
|---|---|---|
| **Cross-Site Scripting (XSS)** | Strict Mermaid rendering security level & HTML sanitization | Mermaid initialized with `securityLevel: 'strict'`. Strips `<script>` tags and `javascript:` URLs from Mermaid code before rendering. |
| **HTML Injection** | Output escaping in theme UI | All dynamic strings in `src/ui/theme.py` (`render_user_story_card`, `render_bento_card`, `render_telemetry_widget`) are passed through `html.escape`. |
| **SQL Sandbox Jailbreak** | Block dangerous SQLite statements & features | Intercepts and denies `ATTACH DATABASE`, `DETACH`, `VACUUM INTO`, and `load_extension`. Restricts execution to safe DDL statements. |
| **Resource Exhaustion (Sandbox DoS)** | Script size limits, statement limits & opcode timeouts | Enforces a maximum 64KB DDL script size, 50 statements maximum, and sets a 100,000 opcode progress handler timeout via `sqlite3.set_progress_handler`. |
| **SQL Injection in Meta Queries** | Identifier quote escaping | Sanitizes table names when querying `PRAGMA table_info` and `PRAGMA index_list`. |
| **Credential & Secret Exposure** | API Key masking & Redaction | `src/utils/security.py` masks API keys (e.g., `AIzaSy...7890`) and strips secrets from user-facing error messages and exception logs. |
| **Prompt Injection & Token DoS** | Input bounding & system instruction defense | Restricts meeting notes input to 50,000 characters at both frontend and backend layers, with adversarial prompt injection defenses in the system prompt. |

---

## 4. Performance & High-Availability Architecture

1. **Thread-Safe LRU & TTL Caching (`src/services/telemetry_cache.py`):**
   - Implements `DeterministicSRSCache` backed by `collections.OrderedDict` with `threading.Lock()` to prevent memory leaks in multi-user Streamlit sessions.
   - Enforces a maximum capacity of 128 items and an expiration TTL of 3,600 seconds (1 hour) with automatic pruning.
   - Preserves snapshot isolation via defensive copying.

2. **Pre-compiled Regexes & AST Caching:**
   - Pre-compiles all static regular expressions across `syntax_validator.py`, `db_sandbox.py`, and `consistency_checker.py`.
   - Memoizes DDL normalization with `@functools.lru_cache(maxsize=256)` on `_sanitize_ddl_for_sqlite()`, eliminating repeated regex overhead on hot paths.

3. **Zero-Redundant Deepcopy:**
   - Optimized cache read/write boundaries in `src/services/ai_generator.py` to eliminate duplicate Pydantic `model_copy(deep=True)` passes, halving memory churn on large documents.

4. **Exponential Backoff with Full Random Jitter:**
   - Implements jittered retry delay: $t = \text{delay} \times 2^{\text{attempt}} + \text{uniform}(0, \text{delay})$, preventing API request synchronization during rate-limiting events.

---

## 5. Industrial Standards & Compliance

- **IEEE 29148:2018:** Systems and software engineering — Life cycle processes — Requirements engineering.
- **BABOK Guide v3:** A Guide to the Business Analysis Body of Knowledge (Requirements Traceability Matrix).
- **ISO/IEC 25010:** System and software quality models for Non-Functional Requirements categorization.
- **3NF / Boyce-Codd Normal Form:** Relational database normalization eliminating partial (2NF) and transitive (3NF) dependencies.
- **Gherkin BDD:** Formal Given-When-Then behavioral acceptance criteria.
