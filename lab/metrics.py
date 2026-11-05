"""Small, dependency-free classification metrics for educational use."""

from collections import Counter
from collections.abc import Hashable, Iterable


def _validate(y_true: Iterable[Hashable], y_pred: Iterable[Hashable]) -> tuple[list[Hashable], list[Hashable]]:
    """Materialize labels and reject malformed input with predictable errors."""
    true = list(y_true)
    pred = list(y_pred)
    if not true:
        raise ValueError("at least one sample is required")
    if len(true) != len(pred):
        raise ValueError("y_true and y_pred must have equal lengths")
    for label in true + pred:
        try:
            hash(label)
        except TypeError as exc:
            raise TypeError("class labels must be hashable") from exc
    return true, pred


def accuracy(y_true: Iterable[Hashable], y_pred: Iterable[Hashable]) -> float:
    """Fraction of correctly classified samples."""
    true, pred = _validate(y_true, y_pred)
    return sum(t == p for t, p in zip(true, pred)) / len(true)


def confusion_counts(y_true: Iterable[Hashable], y_pred: Iterable[Hashable]) -> dict[tuple[Hashable, Hashable], int]:
    """Count each (actual_label, predicted_label) pair."""
    true, pred = _validate(y_true, y_pred)
    return dict(Counter(zip(true, pred)))
