# DevForge AI — human-reviewed daily development (pilot)

A practical proof of concept for an AI-assisted GitHub portfolio. **Once a day**, a GitHub Actions workflow chooses the next task in a curated backlog, invokes OpenAI Codex in a read-only-repository job, runs tests, checks which files changed, and passes a patch to an isolated publishing job that **opens a pull request**. Nothing is auto-merged.

## First app: Python classification metrics lab

This repository includes a real Python package (`lab/`), unit tests (`tests/`), and three incremental milestones (`tasks/backlog.json`) to show how a single repository can evolve through real, reviewable improvements.

## Architecture

`daily schedule → check pending PR → choose task → Codex (read-only GitHub permissions) → changed-file guard → unit tests → patch artifact → isolated publisher (write token) → mark task complete on branch → open PR → human review/merge`

A PR can be generated only while there is no other open automation PR. Merging a PR updates `tasks/completed.json` on the default branch, allowing the next day's run to select the next task. This design does **not** create filler commits on days when no genuine work can be done.

## Quick start

1. Create a **new** empty public repository named `devforge-ai` on your GitHub account (do **not** initialize it with a README). Keep existing code repositories separate.
2. On your computer, extract this package, enter the extracted folder, and run:
   ```bash
   git init -b main
   git add .
   git commit -m "chore: initialize DevForge AI pilot"
   git remote add origin https://github.com/Kuhananth-Chandrapalan/devforge-ai.git
   git push -u origin main
   ```
3. Add a repository Actions secret named **`OPENAI_API_KEY`** in Settings → Secrets and variables → Actions. Generate the key via the official OpenAI API dashboard. **Never paste an API key into chat or commit it to Git.** The Codex Action requires an API key; ChatGPT subscription access is separate from API billing.
4. Under Settings → Actions → General, enable **Allow GitHub Actions to create and approve pull requests** if that option is available. Keep repository Actions workflow permissions scoped appropriately.
5. Optional but recommended for CI triggered by agent-created PRs: add `DEVFORGE_GH_TOKEN` as a **fine-grained** token restricted to this single repo, with **Contents: Read/Write** and **Pull requests: Read/Write**. Without it, the default `GITHUB_TOKEN` can create the PR but PR-triggered workflow runs will need your explicit **Approve workflows to run** action (GitHub’s current `GITHUB_TOKEN` behavior). The daily workflow still runs tests before publishing; review the diff and arrange an independent CI check before merging.
6. Open the repository's **Actions → Daily Codex Development → Run workflow** to test manually before relying on the daily schedule.
7. Review the resulting PR and merge it manually only when the implementation is correct. The next task is then available on the next scheduled run.

> Important: Protecting `main` from direct pushes is recommended. GitHub's ruleset/branch-protection features and the ability to require reviews vary by plan and repository visibility. For a solo owner, enforce **manual merge**, not a mandatory review by yourself (GitHub won't normally count self-approval as an independent review). No auto-merge is configured.

## Scheduling

The schedule runs daily at **08:17 Asia/Colombo**. Scheduled GitHub workflows may be delayed and generally run from the default branch. If GitHub disables idle scheduled workflows, re-enable them in repository Actions.

## Run local checks

```bash
python -m unittest discover -s tests -v
python -m compileall -q lab tests scripts
```

## Customizing your portfolio

Add curated tasks to `tasks/backlog.json`, one item per meaningful reviewable feature, and keep `tasks/completed.json` under version control. The trust boundary is intentional: only trusted humans should edit the backlog and automation workflows. Codex may edit only `lab/`, `tests/`, `docs/`.

Once this pilot works, use separate repositories for an ML experiments project, a Laravel API project and an AI agent project, with the same human-reviewed PR pattern. Schedule each independently or add a central coordinator with repository-scoped GitHub App credentials. Do not grant a single AI process broad organization-wide write access.

## Security and limitations

- Generated code can be wrong or malicious; review every diff.
- The guard detects file changes outside allowlisted paths. It is **not** an exhaustive security sandbox and cannot prove source-code safety.
- Codex uses `permission-profile: ':workspace'` with the action's default sudo reduction; do not give it a repository write token. A separate publishing job with repository-scoped write permissions handles Git credentials; the Codex job has only read permissions.
- Runs can fail because of API quota, billing limits, action compatibility or model output; they fail closed without a PR if tests/guard checks fail.
- Backlog tasks are trusted input. Do not build prompts from arbitrary public issue comments without additional controls.
- Be careful not to commit sensitive or proprietary training data.
- GitHub contribution graph activity is not guaranteed for bot-authored commits. The portfolio goal is meaningful work, not fake activity.
- For production, pin third-party Actions to reviewed commit SHAs, set API spending limits, add dependency/security scanners and use an isolated GitHub App identity.

## Docs

See `docs/guide.md` and `AGENTS.md` for project and agent rules.
