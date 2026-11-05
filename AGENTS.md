# Codex project rules

This repository is a human-reviewed, incremental Python portfolio project.

- Only implement the single task in the supplied prompt.
- Edit only `lab/`, `tests/`, and `docs/`.
- Never change `.github/`, `scripts/`, `tasks/`, `AGENTS.md`, project configuration or secrets.
- Add deterministic unit tests for each new feature.
- Keep runtime dependencies at zero; use Python 3.11+ standard library.
- Do not fetch external data, access the network, commit, push, or open PRs.
- Use readable Python with type hints where useful.
- Keep behavior correct in edge cases, especially empty or invalid inputs.
