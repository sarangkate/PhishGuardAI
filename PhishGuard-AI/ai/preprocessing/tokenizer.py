from typing import Dict


def tokenize_for_bert(tokenizer, text: str, max_length: int = 512) -> Dict:
    return tokenizer(
        text or "",
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=max_length,
    )
