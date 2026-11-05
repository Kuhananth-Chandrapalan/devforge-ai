"""Record successful task completion inside the PR, not on the default branch."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mark_complete(task_id: str, root: Path = ROOT) -> None:
    backlog = json.loads((root / "tasks/backlog.json").read_text())
    ids = {task["id"] for task in backlog}
    if task_id not in ids:
        raise ValueError("unknown task ID")
    path = root / "tasks/completed.json"
    completed = json.loads(path.read_text())
    if task_id in completed:
        raise ValueError("task already marked complete")
    completed.append(task_id)
    path.write_text(json.dumps(completed, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/mark_complete.py TASK_ID")
    mark_complete(sys.argv[1])
