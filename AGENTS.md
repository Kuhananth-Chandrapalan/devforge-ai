# DevForge Free AI agent constraints

An external AI model may propose a bounded feature as a JSON list of file edits.
Only `lab/`, `tests/`, and `docs/` changes are permitted. These must be reviewed.

- Implement the single trusted backlog task in the generated prompt.
- Make a real change in `lab/` with deterministic unit tests and docs.
- Never change `.github/`, `scripts/`, `tasks/`, dependencies, credentials or settings.
- Never send private code or personal data to a free-tier model. The free-tier
  provider may use inputs to improve its services.
- Never install packages or make external network calls from generated code.
- Do not add filler commits just to change a contribution graph.
- No automatic merge is allowed.
