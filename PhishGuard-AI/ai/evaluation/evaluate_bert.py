"""Evaluate the configured phishing BERT model on a held-out external dataset.

This script intentionally evaluates on a dataset different from the model's published
training corpus when possible. It does not copy the model author's reported metrics
into our project metrics.
"""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()

    try:
        from datasets import load_dataset
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        from ai.models.bert_model import predict_text
    except ImportError as exc:
        raise SystemExit(f"Install AI evaluation dependencies first: {exc}")

    dataset = load_dataset("cybersectony/PhishingEmailDetectionv2.0", split="test")
    rows = []
    for row in dataset:
        label = int(row["labels"])
        if label not in (0, 1):
            continue
        rows.append((row["content"], label))
        if len(rows) >= args.limit:
            break

    if not rows:
        raise SystemExit("No binary email rows were found in the evaluation dataset.")

    y_true, y_pred = [], []
    for text, label in rows:
        result = predict_text(text)
        y_true.append(label)
        y_pred.append(1 if result["classification"] == "Phishing" else 0)

    metrics = {
        "samples": len(rows),
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }

    output = Path(__file__).resolve().parent / "bert_evaluation.json"
    output.write_text(__import__("json").dumps(metrics, indent=2), encoding="utf-8")
    print(__import__("json").dumps(metrics, indent=2))
    print(f"Saved evaluation to {output}")


if __name__ == "__main__":
    main()
