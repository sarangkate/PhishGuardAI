import os
from pathlib import Path

MODEL_NAME = os.getenv("BERT_MODEL_NAME", "ElSlay/BERT-Phishing-Email-Model")
CACHE_DIR = Path(os.getenv("BERT_MODEL_CACHE", Path(__file__).resolve().parents[1] / "models" / "phishing_bert"))


def main():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading/loading model: {MODEL_NAME}")
    AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=str(CACHE_DIR))
    AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, cache_dir=str(CACHE_DIR))
    print(f"Model is cached under: {CACHE_DIR}")


if __name__ == "__main__":
    main()
