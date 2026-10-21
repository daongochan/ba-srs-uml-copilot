# Git & GitHub Collaboration Rules

## 1. Branch Strategy
- **`main`**: Production stable branch. Never commit directly to `main` for experimental changes.
- **Working Branches**: Always create feature or fix branches from `main`:
  - `feat/<feature-name>`: New feature or capability.
  - `fix/<bug-name>`: Bug fix or corrective patch.
  - `chore/<task-name>`: Tooling, dependency, or configuration updates.
  - `docs/<topic-name>`: Documentation, guides, or changelog updates.
  - `style/<scope>`: UI, UX, styling, or formatting changes.

## 2. Commit Message Conventions (Conventional Commits)
Format: `<type>(<scope>): <short imperative description>`

- **Types**:
  - `feat`: A new user-facing feature.
  - `fix`: A bug fix.
  - `docs`: Documentation only changes.
  - `style`: Changes that do not affect code logic (white-space, formatting, CSS).
  - `refactor`: Code change that neither fixes a bug nor adds a feature.
  - `test`: Adding missing tests or correcting existing tests.
  - `chore`: Changes to build process, auxiliary tools, or libraries.

- **Commit Principles**:
  - Small, atomic commits (one logical change per commit).
  - Message must explain **why** the change was made, not just **what**.
  - Always write commit messages and pull request descriptions in English.

## 3. Pull Request (PR) Workflow
1. Run local validation before pushing (`pytest` and `ruff check`).
2. Push branch to `origin`: `git push -u origin <branch-name>`.
3. Open a Pull Request using `.github/pull_request_template.md`.
4. Check GitHub Actions CI status; all checks must pass green before merge.
5. **No Self-Merge**: Never merge into `main` without explicit confirmation from the repository owner.

## 4. Forbidden Operations
- Never run `git push --force` or `git push -f` on any shared branch.
- Never run `git reset --hard` without explicit user confirmation.
- Never delete remote branches without user approval.
- Never skip pre-commit hooks (`--no-verify`) unless strictly instructed for emergency diagnosis.
