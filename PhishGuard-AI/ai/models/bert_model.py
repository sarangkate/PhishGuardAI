import os
from pathlib import Path
from typing import Any, Dict, Optional


MODEL_NAME = os.getenv("BERT_MODEL_NAME", "ElSlay/BERT-Phishing-Email-Model")
MODEL_CACHE = Path(
    os.getenv(
        "BERT_MODEL_CACHE",
        str(Path(__file__).resolve().parent / "phishing_bert"),
    )
)

_model = None
_tokenizer = None
_load_error: Optional[str] = None


def _find_local_snapshot() -> Optional[Path]:
    """Find a complete locally cached Hugging Face snapshot, if one exists."""
    if not MODEL_CACHE.exists():
        return None

    candidates = sorted(
        (
            path
            for path in MODEL_CACHE.glob("models--*/snapshots/*")
            if path.is_dir()
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    for snapshot in candidates:
        required = ("config.json", "tokenizer.json", "vocab.txt", "model.safetensors")
        if all((snapshot / name).is_file() for name in required):
            return snapshot

    return None


def load_bert_model():
    global _model, _tokenizer, _load_error

    if _model is not None and _tokenizer is not None:
        return _tokenizer, _model

    if _load_error is not None:
        raise RuntimeError(_load_error)

    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        local_snapshot = _find_local_snapshot()

        if local_snapshot is not None:
            # Loading directly from the snapshot avoids ambiguity between a
            # local cache directory and a model directory.
            model_source = str(local_snapshot)
            load_kwargs = {"local_files_only": True}
        else:
            MODEL_CACHE.mkdir(parents=True, exist_ok=True)
            model_source = MODEL_NAME
            load_kwargs = {"cache_dir": str(MODEL_CACHE)}

        _tokenizer = AutoTokenizer.from_pretrained(model_source, **load_kwargs)
        _model = AutoModelForSequenceClassification.from_pretrained(
            model_source,
            **load_kwargs,
        )
        _model.eval()
        _load_error = None
        return _tokenizer, _model

    except Exception as exc:
        _model = None
        _tokenizer = None
        _load_error = (
            "BERT model could not be loaded. Install the AI dependencies and "
            f"ensure the model '{MODEL_NAME}' is available. Original error: {exc}"
        )
        raise RuntimeError(_load_error) from exc


def _phishing_label(model) -> int:
    """Resolve the phishing class from model metadata, with a safe binary fallback."""
    id2label = getattr(model.config, "id2label", {}) or {}

    for idx, label in id2label.items():
        if any(
            word in str(label).lower()
            for word in ("phish", "malicious", "fraud", "spam")
        ):
            return int(idx)

    # The selected upstream model uses LABEL_0/LABEL_1, where LABEL_1 is the
    # phishing class. Keep this fallback explicit rather than pretending the
    # generic LABEL names are self-describing.
    return 1


def predict_text(text: str, max_length: int = 512) -> Dict[str, Any]:
    import torch

    tokenizer, model = load_bert_model()

    inputs = tokenizer(
        text or "",
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=max_length,
    )

    with torch.inference_mode():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1)[0]

    predicted_id = int(torch.argmax(probabilities).item())
    phishing_id = _phishing_label(model)
    phishing_probability = float(probabilities[phishing_id].item())
    confidence = float(probabilities[predicted_id].item())
    label = str(
        (getattr(model.config, "id2label", {}) or {}).get(
            predicted_id,
            predicted_id,
        )
    )

    return {
        "available": True,
        "model": MODEL_NAME,
        "predicted_label": label,
        "predicted_id": predicted_id,
        "phishing_probability": round(phishing_probability, 6),
        "confidence": round(confidence, 6),
        "classification": (
            "Phishing" if predicted_id == phishing_id else "Legitimate"
        ),
    }
