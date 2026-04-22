# Copilot Instructions

All code generation, file creation, and terminal commands MUST be scoped to the
project directory: `voice2voice-ai/`.

Never suggest commands that:
- Write to /tmp, ~, /usr, or any path outside the project
- Install packages globally (always use `.venv` via `uv`)
- Modify system-level audio or OS configurations

Use `uv` for all Python dependency management — never `pip` or `python -m venv`.

## Code Contribution

### Branching & Workflow

1. **Create a feature branch** before making changes:
   - VS Code task: `git-branch` (prompts for branch name)
   - Terminal: `bash scripts/git_ops.sh branch feature/my-feature`
   - Convention: `feature/`, `fix/`, `chore/` prefixes

2. **Make changes** — commit early and often with clear messages:
   ```bash
   git add -A && git commit -m "feat: add awesome feature"
   ```

3. **Run quality checks** before pushing:
   - VS Code task: `check-all` (runs format-check → lint → tests in sequence)
   - Terminal: `uv run ruff format --check src/ tests/ && uv run ruff check src/ tests/ && uv run pytest`

4. **Push** your branch to GitHub:
   - VS Code task: `git-push`
   - Terminal: `bash scripts/git_ops.sh push`

5. **Pull** latest changes from origin:
   - VS Code task: `git-pull`
   - Terminal: `bash scripts/git_ops.sh pull`

6. **Create a Pull Request**:
   - VS Code task: `git-pr` (prompts for title, body, and base branch)
   - Terminal: `bash scripts/git_ops.sh pr "PR title" "Description" main`
   - The script auto-pushes the branch before creating the PR.
   - PRs target `main` by default.

### GitHub Authentication

- A GitHub PAT is stored in `.env` as `GH_PAT`.
- The helper script `scripts/git_ops.sh` reads `GH_PAT` from `.env` at runtime
  — secrets never appear in task definitions or command history.
- `.env` is git-ignored; never commit it.

### VS Code Tasks & Agent Auto-Approval

All project tasks are defined in `.vscode/tasks.json`. The workspace
`settings.json` enables `chat.tools.autoApprove` for key Copilot tools
(file create/edit/read, list directory, and **run task**). This means agents
**can and should run these tasks directly** without prompting the user for
confirmation.

#### Available Tasks

| Task             | Description                                        |
|------------------|----------------------------------------------------|
| `sync-deps`      | Install/sync all dependencies (`uv sync --extra dev`) |
| `add-dep`        | Add a new dependency via `uv`                      |
| `test`           | Run the full test suite with `pytest`               |
| `test-verbose`   | Run tests with verbose output and short tracebacks  |
| `test-file`      | Run a specific test file                            |
| `lint`           | Lint `src/` and `tests/` with `ruff`                |
| `lint-fix`       | Auto-fix lint issues with `ruff`                    |
| `format`         | Format `src/` and `tests/` with `ruff`              |
| `format-check`   | Check formatting without making changes             |
| `check-all`      | Run format-check → lint → tests in sequence         |
| `run-app`        | Run the voice-app entry point                       |
| `clean`          | Remove build artifacts and caches                   |
| `git-push`       | Push current branch to GitHub                       |
| `git-pull`       | Pull latest from GitHub for current branch          |
| `git-pr`         | Create a pull request from current branch           |
| `git-branch`     | Create and switch to a new branch                   |

> **Agents**: Prefer running these tasks over manually typing the equivalent
> shell commands. Tasks that require user input (e.g., `add-dep`, `test-file`,
> `git-pr`, `git-branch`) will prompt for the necessary values. All other tasks
> run without interaction.

### Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `chore:` — maintenance (deps, CI, configs)
- `docs:` — documentation only
- `refactor:` — code restructuring without behavior change
- `test:` — adding or updating tests


### End-to-end Feature Development Workflow
1. **Create a feature branch**: `feature/awesome-feature`
2. **Implement the feature** with regular commits.
3. **Run quality checks** (format, lint, tests) before pushing.
4. **Push the branch** to GitHub.
5. **Create a Pull Request** targeting `main`.
6. **Request reviews** from user "aranjandev".