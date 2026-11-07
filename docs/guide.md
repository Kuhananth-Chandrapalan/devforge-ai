# Python classification metrics lab

The `lab` package uses only Python's standard library. This pilot provides
accuracy, confusion counts, binary classification metrics (precision, recall, F1),
per-class metrics, and macro-F1.

```python
from lab import (
    accuracy,
    binary_classification_metrics,
    confusion_counts,
    macro_f1,
    per_class_metrics,
)

actual = ["cat", "dog", "cat", "dog"]
predicted = ["cat", "cat", "cat", "dog"]
print(accuracy(actual, predicted))  # 0.75
print(confusion_counts(actual, predicted))

# Binary classification metrics
metrics = binary_classification_metrics(actual, predicted, positive_label="dog")
print(metrics)
# {'precision': 1.0, 'recall': 0.5, 'f1': 0.6666666666666666, 'tp': 1, 'fp': 0, 'fn': 1, 'tn': 2}

# Multiclass per-class metrics and macro-F1
actual_multi = ["a", "b", "c", "a"]
predicted_multi = ["a", "c", "c", "b"]
print(per_class_metrics(actual_multi, predicted_multi))
print(macro_f1(actual_multi, predicted_multi))
```

The daily free-tier AI editor is designed to propose the following milestones: precision/recall/F1, multiclass reporting, and a JSON CLI. Every change requires human PR review.

Run checks with:

```bash
python -m unittest discover -s tests -v
python -m compileall -q lab tests
```
