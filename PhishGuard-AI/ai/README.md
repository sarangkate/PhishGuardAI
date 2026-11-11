# PhishGuardAI AI subsystem

Steps 30–39 implement the AI and decision layer:

- Step 30: BERT environment and model loading
- Step 31: email text cleaning and tokenization
- Step 32: BERT content analysis
- Step 33: external evaluation script
- Step 34: combined analysis pipeline
- Step 35: evidence structure
- Step 36: decision engine
- Step 37: risk score and model confidence separation
- Step 38: evidence-based explanations
- Step 39: recommendation generation

The BERT model is downloaded automatically by Transformers when first used, or explicitly with:

`python -m ai.scripts.download_model`


## Decision scoring

The final 0–100 risk score is not the same as model confidence. The decision engine uses 70% of the BERT phishing probability and 30% of the structured sender/URL/header evidence score. Classification thresholds are 0–34 Legitimate, 35–69 Suspicious, and 70–100 Phishing. The result is always generated from runtime analysis; no score or warning is hardcoded.
