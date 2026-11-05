import unittest

from lab.metrics import accuracy, confusion_counts


class TestMetrics(unittest.TestCase):
    def test_accuracy(self):
        self.assertEqual(accuracy([1, 0, 1, 1], [1, 0, 0, 1]), 0.75)

    def test_accuracy_strings(self):
        self.assertEqual(accuracy(["cat", "dog"], ["cat", "dog"]), 1.0)

    def test_confusion_counts(self):
        self.assertEqual(
            confusion_counts(["a", "a", "b"], ["a", "b", "b"]),
            {("a", "a"): 1, ("a", "b"): 1, ("b", "b"): 1},
        )

    def test_empty_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one sample"):
            accuracy([], [])

    def test_mismatched_lengths(self):
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            confusion_counts([1, 2], [1])

    def test_unhashable_rejected(self):
        with self.assertRaisesRegex(TypeError, "hashable"):
            accuracy([[1]], [[1]])

    def test_accepts_generators(self):
        self.assertEqual(accuracy((i for i in [0, 1]), (i for i in [0, 0])), 0.5)


if __name__ == "__main__":
    unittest.main()
