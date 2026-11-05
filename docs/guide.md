# Python classification metrics lab

The `lab` package uses only Python's standard library. This pilot begins with
accuracy and the counts of observed `(actual, predicted)` label pairs.

```python
from lab import accuracy, confusion_counts

actual = ["cat", "dog", "cat", "dog"]
predicted = ["cat", "cat", "cat", "dog"]
print(accuracy(actual, predicted))  # 0.75
print(confusion_counts(actual, predicted))
```

Later milestones add precision/recall/F1, multiclass reporting, and a JSON CLI.

Run checks with:

```bash
python -m unittest discover -s tests -v
python -m compileall -q lab tests
```
