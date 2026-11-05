import json
import tempfile
import unittest
from pathlib import Path

from scripts.mark_complete import mark_complete
from scripts.select_task import create_prompt, pending_task


class TestOrchestrator(unittest.TestCase):
    def test_selection_matches_uncompleted_backlog(self):
        root = Path(__file__).resolve().parents[1]
        tasks = json.loads((root / "tasks/backlog.json").read_text())
        completed = set(json.loads((root / "tasks/completed.json").read_text()))
        expected = next((t for t in tasks if t["id"] not in completed), None)
        self.assertEqual(pending_task(), expected)

    def test_prompt_honors_edit_constraints(self):
        prompt = create_prompt({"id": "a-first", "title": "Sample", "instructions": "Implement sample", "acceptance": ["Add tests"]})
        self.assertIn("lab/, tests/, and docs/", prompt)
        self.assertIn("do not", prompt.lower())

    def test_completion_moves_to_next_task(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "tasks").mkdir()
            tasks = [{"id": "a-first", "title": "a", "instructions": "a", "acceptance": ["a"]},
                     {"id": "b-second", "title": "b", "instructions": "b", "acceptance": ["b"]}]
            (root / "tasks/backlog.json").write_text(json.dumps(tasks))
            (root / "tasks/completed.json").write_text("[]")
            self.assertEqual(pending_task(root)["id"], "a-first")
            mark_complete("a-first", root)
            self.assertEqual(pending_task(root)["id"], "b-second")


if __name__ == "__main__":
    unittest.main()
