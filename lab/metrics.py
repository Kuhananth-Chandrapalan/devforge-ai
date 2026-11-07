"""Small, dependency-free classification metrics for educational use."""

from collections import Counter
from collections.abc import Hashable, Iterable
from typing import Any, Union


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


def binary_classification_metrics(
    y_true: Iterable[Hashable],
    y_pred: Iterable[Hashable],
    positive_label: Hashable = 1,
) -> dict[str, Union[float, int]]:
    """Compute precision, recall, F1, and raw confusion counts for a binary target."""
    try:
        hash(positive_label)
    except TypeError as exc:
        raise TypeError("class labels must be hashable") from exc
    true, pred = _validate(y_true, y_pred)
    tp = fp = fn = tn = 0
    for t, p in zip(true, pred):
        t_pos = t == positive_label
        p_pos = p == positive_label
        if t_pos and p_pos:
            tp += 1
        elif not t_pos and p_pos:
            fp += 1
        elif t_pos and not p_pos:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def per_class_metrics(y_true: Iterable[Hashable], y_pred: Iterable[Hashable]) -> dict[Hashable, dict[str, float]]:
    """Compute precision, recall, f1, and support for every label found in inputs.

    Labels are ordered by their first occurrence in y_true or y_pred without sorting.
    """
    true, pred = _validate(y_true, y_pred)
    labels = []
    seen = set()
    for label in true + pred:
        if label not in seen:
            seen.add(label)
            labels.append(label)

    results = {}
    for label in labels:
        tp = 0
        fp = 0
        fn = 0
        support = 0
        for t, p in zip(true, pred):
            if t == label:
                support += 1
            if t == label and p == label:
                tp += 1
            elif t != label and p == label:
                fp += 1
            elif t == label and p != label:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        results[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }

    return results


def macro_f1(y_true: Iterable[Hashable], y_pred: Iterable[Hashable]) -> float:
    """Compute unweighted average F1 score across all labels found in inputs."""
    class_metrics = per_class_metrics(y_true, y_pred)
    if not class_metrics:
        return 0.0
    return sum(metrics["f1"] for metrics in class_metrics.values()) / len(class_metrics)
