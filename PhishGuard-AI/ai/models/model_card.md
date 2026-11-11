# PhishGuardAI BERT model

Default model: `ElSlay/BERT-Phishing-Email-Model`

Purpose: binary phishing-vs-legitimate email-content classification.

The model is a fine-tuned BERT model intended for phishing email detection. Its Hugging Face model card reports that it was fine-tuned for phishing/legitimate email classification. The model is downloaded at runtime into the local Hugging Face/model cache and is intentionally not committed into this repository because model weights are hundreds of megabytes.

Upstream reference: https://huggingface.co/ElSlay/BERT-Phishing-Email-Model

Important: upstream-reported evaluation metrics are not PhishGuardAI's measured production metrics. PhishGuardAI has its own evaluation script (`ai/evaluation/evaluate_bert.py`) so project metrics can be measured on an external test dataset.
