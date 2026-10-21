# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **MCP Server Configurations**: Global and workspace MCP templates for `github`, `context7`, and `sequential-thinking`.
- **Engineering Rules**: Agent standards in `.agents/rules/` (`00-project.md`, `01-git-github.md`, `02-security.md`).
- **Automated Workflows**: `/ship` workflow for pre-flight testing and deployment; `/fix-ci` workflow for autonomous CI repair.
- **Quality Gates**: Ruff linter and formatter configuration in `pyproject.toml` with zero false-positives.
- **Pre-commit Automation**: `.pre-commit-config.yaml` with trailing-whitespace, YAML validation, and Ruff hooks.
- **CI/CD Enhancements**: GitHub Actions multi-version Python matrix (3.10–3.13) with pip caching and compile verification.
- **Repository Governance**: `.github/dependabot.yml` and `.github/pull_request_template.md`.

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
