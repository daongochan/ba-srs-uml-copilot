# Project Standards & Definition of Done

## 1. Project Overview & Tech Stack
- **System**: BA & System Architect Copilot (`ba-srs-uml-copilot`).
- **Domain**: Enterprise B2B SaaS & Developer Workbench for converting raw stakeholder meeting notes into IEEE 29148 SRS, UML Sequence/State diagrams, 3NF ERD, and SQLite verified SQL DDL.
- **Language**: Python 3.13 (Virtual Environment: `.\.venv\Scripts\python.exe`).
- **Web Framework**: Streamlit (v1.66+).
- **Core AI Engine**: Google GenAI SDK (`google-genai` v2.31+) with Gemini 2.5/3.8 Flash models.
- **Data Validation & Schemas**: Pydantic v2 (Strict Schema Validation & Serialization).
- **SQL Parsing & In-Memory Sandbox**: `sqlglot` AST engine and Python `sqlite3` in-memory database (`:memory:`).
- **Diagram Engine**: Mermaid.js (Sequence, State Machine, ERD) rendered via custom interactive SVG canvas.
- **Design Intelligence**: UI/UX Pro Max tokens and theme (`design-system/MASTER.md` & `src/ui/theme.py`).

## 2. Directory Structure
```
ba-srs-uml-copilot/
├── .agent/              # Skill catalogs and UI-UX intelligence
├── .agents/             # Agent rules, workflows, and MCP configurations
├── .github/             # GitHub Actions CI workflows, dependabot, PR templates
├── design-system/       # Master design tokens & UX guidelines (Source of Truth)
├── docs/                # Architecture documentation & diagrams
├── src/                 # Application source code
│   ├── data/            # Sample scenario datasets
│   ├── models/          # Pydantic SRS and validation schemas
│   ├── services/        # AI generator, exporters, telemetry & caching
│   ├── ui/              # Enterprise theme tokens, header stepper, bento cards
│   ├── validators/      # Syntax, DB sandbox, linter, consistency checker
│   └── app.py           # Streamlit workbench entrypoint
└── tests/               # Pytest test suite (100% test coverage)
```

## 3. Standard Commands
Always invoke tools through the local virtual environment:
- **Run Application**:
  ```powershell
  .\.venv\Scripts\python.exe -m streamlit run src/app.py
  ```
- **Execute Test Suite**:
  ```powershell
  .\.venv\Scripts\python.exe -m pytest -v --tb=short
  ```
- **Run Linter (Ruff)**:
  ```powershell
  .\.venv\Scripts\python.exe -m ruff check .
  ```
- **Auto-Format Code (Ruff)**:
  ```powershell
  .\.venv\Scripts\python.exe -m ruff format .
  ```

## 4. Definition of Done (DoD)
Every task or feature is considered complete ONLY when:
1. **Application Integrity**: No application source code is altered unless explicitly requested.
2. **Deterministic Quality**: 100% of unit and integration tests pass (`pytest` exit code 0).
3. **Clean Linting**: `ruff check .` returns 0 warnings and 0 errors.
4. **Resilience**: Session state compatibility is preserved (no `AttributeError` on missing attributes).
5. **No Secrets**: No API keys, tokens, or sensitive hashes are committed into Git.
6. **Documentation**: Any behavior or schema changes are recorded in `CHANGELOG.md` and `README.md`.
