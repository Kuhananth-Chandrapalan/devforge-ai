import unittest

from lab.metrics import accuracy, binary_classification_metrics, confusion_counts


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
        with self.assertRaisesRegex(ValueError, "at least one sample"):
            binary_classification_metrics([], [])

    def test_mismatched_lengths(self):
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            confusion_counts([1, 2], [1])
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            binary_classification_metrics([1, 0], [1])

    def test_unhashable_rejected(self):
        with self.assertRaisesRegex(TypeError, "hashable"):
            accuracy([[1]], [[1]])
        with self.assertRaisesRegex(TypeError, "hashable"):
            binary_classification_metrics([1], [1], positive_label=[1])

    def test_accepts_generators(self):
        self.assertEqual(accuracy((i for i in [0, 1]), (i for i in [0, 0])), 0.5)

    def test_binary_metrics_perfect(self):
        res = binary_classification_metrics([1, 0, 1, 0], [1, 0, 1, 0])
        self.assertEqual(
            res,
            {
                "precision": 1.0,
                "recall": 1.0,
                "f1": 1.0,
                "tp": 2,
                "fp": 0,
                "fn": 0,
                "tn": 2,
            },
        )

    def test_binary_metrics_false_positives(self):
        res = binary_classification_metrics([0, 0, 1], [1, 0, 1])
        self.assertEqual(res["tp"], 1)
        self.assertEqual(res["fp"], 1)
        self.assertEqual(res["fn"], 0)
        self.assertEqual(res["tn"], 1)
        self.assertEqual(res["precision"], 0.5)
        self.assertEqual(res["recall"], 1.0)
        self.assertAlmostEqual(res["f1"], 2 / 3)

    def test_binary_metrics_false_negatives(self):
        res = binary_classification_metrics([1, 1, 0], [0, 1, 0])
        self.assertEqual(res["tp"], 1)
        self.assertEqual(res["fp"], 0)
        self.assertEqual(res["fn"], 1)
        self.assertEqual(res["tn"], 1)
        self.assertEqual(res["precision"], 1.0)
        self.assertEqual(res["recall"], 0.5)
        self.assertAlmostEqual(res["f1"], 2 / 3)

    def test_binary_metrics_zero_denominators(self):
        # No predicted positives: tp + fp == 0 -> precision denominator is 0
        res = binary_classification_metrics([1, 0], [0, 0], positive_label=1)
        self.assertEqual(res["precision"], 0.0)
        self.assertEqual(res["recall"], 0.0)
        self.assertEqual(res["f1"], 0.0)
        self.assertEqual(res["tp"], 0)
        self.assertEqual(res["fp"], 0)
        self.assertEqual(res["fn"], 1)
        self.assertEqual(res["tn"], 1)

        # No actual positives: tp + fn == 0 -> recall denominator is 0
        res2 = binary_classification_metrics([0, 0], [1, 0], positive_label=1)
        self.assertEqual(res2["precision"], 0.0)
        self.assertEqual(res2["recall"], 0.0)
        self.assertEqual(res2["f1"], 0.0)
        self.assertEqual(res2["tp"], 0)
        self.assertEqual(res2["fp"], 1)
        self.assertEqual(res2["fn"], 0)
        self.assertEqual(res2["tn"], 1)

        # Both zero
        res3 = binary_classification_metrics([0, 0], [0, 0], positive_label=1)
        self.assertEqual(res3["precision"], 0.0)
        self.assertEqual(res3["recall"], 0.0)
        self.assertEqual(res3["f1"], 0.0)
        self.assertEqual(res3["tp"], 0)
        self.assertEqual(res3["fp"], 0)
        self.assertEqual(res3["fn"], 0)
        self.assertEqual(res3["tn"], 2)

    def test_binary_metrics_arbitrary_hashable_labels(self):
        res = binary_classification_metrics(
            [("cat", 1), ("dog", 2)],
            [("cat", 1), ("cat", 1)],
            positive_label=("cat", 1),
        )
        self.assertEqual(res["tp"], 1)
        self.assertEqual(res["fp"], 1)
        self.assertEqual(res["fn"], 0)
        self.assertEqual(res["tn"], 0)
        self.assertEqual(res["precision"], 0.5)
        self.assertEqual(res["recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
