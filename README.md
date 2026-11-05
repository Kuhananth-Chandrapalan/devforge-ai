# DevForge AI — Free-tier daily development starter

**No paid OpenAI API key required.** The original Codex API workflow has been replaced with a small Gemini free-tier AI editor. It is **not** Codex: it is an alternative provider for unattended GitHub Actions. GitHub-hosted Actions standard runners are free for public repositories, while Google's Gemini API has per-account free-tier usage and availability limits. The workflow fails (no PR) if it hits a quota or validation error; never enable paid billing for the Gemini project if you require strictly $0 spending.

## What runs every day

`GitHub schedule → choose approved backlog task → Gemini free-tier generateContent → validate file allowlist → unit tests → transfer reviewed-scope patch → separate publisher → open PR → manual review/merge`

The first pilot is a Python ML classification metrics library. A limited backlog creates genuine incremental functionality. One PR is opened at most until it has been reviewed, so there may be days without commits.

## Setup for a GitHub public repository

1. If this is a new repo, create `devforge-ai` as a **public** GitHub repository, without an initial README.
2. Extract the files into the repo. If you previously pushed the paid starter, **delete `.github/workflows/daily-codex.yml`** (this version already omits it), then copy the updated files and commit. See below.
3. Visit **https://aistudio.google.com/apikey**, create a Google AI Studio API key on a **Free Tier** project, and **do not enable billing**. Supported free-tier models and limits change; this starter defaults to `gemini-3.8-flash`. You can change `GEMINI_MODEL` in the workflow if necessary.
4. In GitHub: `Settings → Secrets and variables → Actions → New repository secret`. Name: `GEMINI_API_KEY`. Paste your key there only. Do **not** add `OPENAI_API_KEY` for this starter.
5. In `Settings → Actions → General`, enable **Allow GitHub Actions to create and approve pull requests**; the workflow itself only *creates* PRs, never approves or merges them.
6. Navigate to `Actions → Daily Free AI Development → Run workflow` to try a manual run. Open its logs and examine the first PR.
7. **Verify validation in the publisher logs (PRs created with the default GitHub Actions token do not automatically trigger a separate `pull_request` workflow); the published PR must still be manually reviewed**, then inspect the source changes before manually merging. The publisher runs the unit tests too before creating any PR.

### Upload on Windows PowerShell (if repo already exists)

Use Git and VS Code, not direct editing via the GitHub web UI. Copy the contents of this ZIP into your existing local `devforge-ai` repo root (where `.git` is located), replacing old files, then run:

```powershell
git status
# Remove the paid workflow from your working tree if it remains:
if (Test-Path .github/workflows/daily-codex.yml) { Remove-Item .github/workflows/daily-codex.yml }
git add -A
git commit -m "Switch DevForge to free Gemini-based daily agent"
git push origin main
```

If you have not pushed the initial repo, you can instead initialize this extracted folder with `git init -b main`, commit, add your GitHub remote, and push. **Do not copy the ZIP's folder over `.git`**; copy only its contents.

## What costs money?

- **Gemini free tier:** $0 within the currently available free quota on an eligible, non-billing-enabled project. Availability and quotas are not guaranteed. **On the free tier, code/prompts may be used by Google to improve its products.** Use public portfolio code only.
- **GitHub Actions:** standard GitHub-hosted runners in **public** repositories are free, subject to GitHub terms and limits. Private repository free allowances differ and can incur charges if exceeded.
- **Codex:** this autonomous workflow is **not Codex**. Codex can be used separately in your IDE/CLI with eligible ChatGPT subscription usage limits, but unattended CI through the OpenAI API is billed separately.

## Run tests locally

```bash
python -m unittest discover -s tests -v
python -m compileall -q lab tests scripts
```

## Boundaries and limitations

- The agent returns **complete source file contents**, not shell commands. No dangerous Git or shell operations are requested from the model.
- The generator rejects path traversal, hidden files, edits outside lab/tests/docs, non-Python/non-Markdown files, duplicate paths and excessive output.
- Generated code is **untrusted** and could be wrong or unsafe. The validation jobs may execute generated tests, but they have no write token or model secret in scope; a separate job publishes the patch.
- Tests alone do not prove correctness or safety. Review every generated file before merging.
- By GitHub design, PRs created with `GITHUB_TOKEN` do not normally trigger new `pull_request` workflow runs. The isolated publisher re-runs all unit tests before opening the PR. For automatically triggered PR CI in a later phase, use a narrowly scoped GitHub App token or another supported event; do not merge without review.
- Once the three starter tasks are completed, add meaningful tasks to the backlog and review the plan.
- GitHub bot-authored commits are not necessarily credited as personal contribution graph activity.
