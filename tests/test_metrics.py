import unittest

from lab.metrics import (
    accuracy,
    binary_classification_metrics,
    confusion_counts,
    macro_f1,
    per_class_metrics,
)


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
        with self.assertRaisesRegex(ValueError, "at least one sample"):
            per_class_metrics([], [])
        with self.assertRaisesRegex(ValueError, "at least one sample"):
            macro_f1([], [])

    def test_mismatched_lengths(self):
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            confusion_counts([1, 2], [1])
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            binary_classification_metrics([1, 0], [1])
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            per_class_metrics([1, 0], [1])
        with self.assertRaisesRegex(ValueError, "equal lengths"):
            macro_f1([1, 0], [1])

    def test_unhashable_rejected(self):
        with self.assertRaisesRegex(TypeError, "hashable"):
            accuracy([[1]], [[1]])
        with self.assertRaisesRegex(TypeError, "hashable"):
            binary_classification_metrics([1], [1], positive_label=[1])
        with self.assertRaisesRegex(TypeError, "hashable"):
            per_class_metrics([[1]], [[1]])

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
        res = binary_classification_metrics([1, 0], [0, 0], positive_label=1)
        self.assertEqual(res["precision"], 0.0)
        self.assertEqual(res["recall"], 0.0)
        self.assertEqual(res["f1"], 0.0)

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

    def test_per_class_metrics_three_class(self):
        y_true = ["a", "b", "c", "a", "b"]
        y_pred = ["a", "c", "c", "b", "b"]
        res = per_class_metrics(y_true, y_pred)
        self.assertEqual(list(res.keys()), ["a", "b", "c"])
        # Class 'a': true=[a, a], pred=[a, b] -> tp=1, fp=0, fn=1, support=2
        self.assertEqual(res["a"]["support"], 2)
        self.assertEqual(res["a"], {"precision": 1.0, "recall": 0.5, "f1": 2 / 3, "support": 2})
        # Class 'b': true=[b, b], pred=[c, b] -> tp=1, fp=1, fn=1, support=2
        self.assertEqual(res["b"]["support"], 2)
        self.assertEqual(res["b"]["precision"], 0.5)
        self.assertEqual(res["b"]["recall"], 0.5)
        self.assertEqual(res["b"]["f1"], 0.5)
        # Class 'c': true=[c], pred=[c] -> tp=1, fp=1, fn=0, support=1
        self.assertEqual(res["c"]["support"], 1)
        self.assertEqual(res["c"]["precision"], 0.5)
        self.assertEqual(res["c"]["recall"], 1.0)
        self.assertAlmostEqual(res["c"]["f1"], 2 / 3)

    def test_per_class_metrics_missing_predicted_class(self):
        y_true = ["a", "b", "c"]
        y_pred = ["a", "a", "a"]
        res = per_class_metrics(y_true, y_pred)
        self.assertIn("b", res)
        self.assertEqual(res["b"], {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 1})
        self.assertIn("c", res)
        self.assertEqual(res["c"], {"precision": 0.0, "recall": 0.0, "f1": 0.0, "support": 1})

    def test_heterogeneous_labels_and_order(self):
        # Heterogeneous labels (int and str) without sorting, preserving first occurrence order
        y_true = [10, "apple", 20]
        y_pred = ["apple", 10, 20]
        res = per_class_metrics(y_true, y_pred)
        self.assertEqual(list(res.keys()), [10, "apple", 20])

    def test_macro_f1(self):
        y_true = ["a", "b", "c"]
        y_pred = ["a", "b", "c"]
        self.assertEqual(macro_f1(y_true, y_pred), 1.0)


if __name__ == "__main__":
    unittest.main()
