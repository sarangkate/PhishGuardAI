from pathlib import Path


def test_ai_testing_documentation_exists():
    assert Path("docs/AI_TESTING.md").exists()
    text = Path("docs/AI_TESTING.md").read_text()
    for metric in ["Accuracy", "Precision", "Recall", "F1", "False positives", "False negatives"]:
        assert metric in text
