"""Pick exactly one uncompleted backlog item and assemble a fixed Codex prompt."""

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pending_task(root: Path = ROOT) -> dict | None:
    backlog = json.loads((root / "tasks/backlog.json").read_text())
    completed = set(json.loads((root / "tasks/completed.json").read_text()))
    for task in backlog:
        task_id = task["id"]
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,79}", task_id):
            raise ValueError(f"invalid task ID: {task_id}")
        if task_id not in completed:
            return task
    return None


def create_prompt(task: dict) -> str:
    items = "\n".join(f"- {criterion}" for criterion in task["acceptance"])
    return f"""You are working on DevForge AI's controlled Python metrics pilot.
Implement ONLY this backlog task, with a real feature and tests:
Task ID: {task['id']}
Title: {task['title']}
Description: {task['instructions']}
Acceptance criteria:
{items}

Mandatory rules:
- Make changes ONLY to files inside lab/, tests/, and docs/.
- Do not alter, remove, or introduce workflows, scripts, tasks, AGENTS.md, dependencies, git metadata, credentials, configuration, or hidden files.
- Do not make network requests or install dependencies. Use only the Python standard library.
- Do not touch or read secrets; do not run destructive commands.
- Implement the narrowest complete solution, add clear tests, and update docs/.
- Use existing public API conventions; ensure python -m unittest discover -s tests -v passes.
- Do not create a pull request, push, or commit. A separate trusted workflow handles publishing.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=".generated/prompt.txt")
    args = parser.parse_args()
    task = pending_task()
    output = Path(args.output)
    if task:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(create_prompt(task), encoding="utf-8")
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write(f"has_task={'true' if task else 'false'}\n")
            if task:
                fh.write(f"task_id={task['id']}\n")
                fh.write(f"task_title={task['title']}\n")
    print(task["id"] if task else "No remaining tasks")


if __name__ == "__main__":
    main()
