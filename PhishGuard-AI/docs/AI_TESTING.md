# PhishGuardAI AI Testing

The AI test suite evaluates behavior on representative legitimate, suspicious and phishing-like email fixtures. It should include different writing styles, link/no-link cases, plain text, HTML, and sender formats.

Metrics to report when an evaluation dataset is actually executed:
- Accuracy
- Precision
- Recall
- F1
- False positives
- False negatives

Project metrics must be based only on the selected unseen evaluation split. Upstream model-card metrics must never be presented as PhishGuardAI metrics.

The BERT model output is evidence for the decision engine. The final PhishGuardAI classification combines model evidence with independently extracted security evidence.
