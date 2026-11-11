"""Evaluate the configured BERT classifier on a small local fixture set.

This is a development sanity check, not a replacement for the official unseen
held-out evaluation in evaluate_bert.py.
"""
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from ai.models.bert_model import predict_text

FIXTURES = [
    (0, "Hi team, the meeting is moved to 3 PM. Please see the agenda in the calendar."),
    (0, "Your monthly statement is ready. You can review it in your normal account portal."),
    (1, "URGENT: Your account will be suspended. Verify your password immediately."),
    (1, "Final warning. Confirm your account now or access will be disabled."),
]


def main():
    y_true, y_pred = [], []
    for expected, text in FIXTURES:
        result = predict_text(text)
        if not result.get("available"):
            raise RuntimeError("BERT model is unavailable")
        y_true.append(expected)
        y_pred.append(int(result["predicted_id"]))

    print({
        "samples": len(y_true),
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "false_positives": sum(a == 0 and b == 1 for a, b in zip(y_true, y_pred)),
        "false_negatives": sum(a == 1 and b == 0 for a, b in zip(y_true, y_pred)),
    })


if __name__ == "__main__":
    main()
