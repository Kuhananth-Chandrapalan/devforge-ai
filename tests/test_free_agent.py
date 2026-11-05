import tempfile
import unittest
from pathlib import Path

from scripts.free_agent import apply_proposal, safe_target


class TestFreeAgent(unittest.TestCase):
    def test_allowlisted_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(safe_target('lab/example.py', root), root / 'lab/example.py')
            for name in ['.github/workflows/ci.yml', '../escape.py',
                         'lab/../../escape.py', 'lab/.secret.py', 'docs/readme.yml',
                         '/tmp/escape.py', 'lab\\escape.py']:
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        safe_target(name, root)

    def test_reject_only_documentation(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                apply_proposal({'files': [{'path': 'docs/guide.md', 'content': 'hello'}]}, Path(directory))

    def test_write_valid_feature(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = apply_proposal({'files': [
                {'path': 'lab/new_feature.py', 'content': 'def answer():\n    return 42\n'},
                {'path': 'tests/test_new_feature.py', 'content': 'import unittest\n'},
            ]}, root)
            self.assertEqual(files, ['lab/new_feature.py', 'tests/test_new_feature.py'])
            self.assertTrue((root / 'lab/new_feature.py').exists())

    def test_reject_bad_edit_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                apply_proposal({'files': [
                    {'path': 'lab/good.py', 'content': 'pass\n'},
                    {'path': '.github/workflows/evil.yml', 'content': 'bad'},
                ]}, root)
            self.assertFalse((root / 'lab/good.py').exists())

    def test_reject_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                apply_proposal({'files': [
                    {'path': 'lab/x.py', 'content': 'one'},
                    {'path': 'lab/x.py', 'content': 'two'},
                ]}, Path(directory))


if __name__ == '__main__':
    unittest.main()
