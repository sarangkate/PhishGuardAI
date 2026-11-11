# AI / Model Documentation

## Model

`ElSlay/BERT-Phishing-Email-Model`

The configured model is a BERT-based binary phishing/legitimate email classifier.

## Role in PhishGuardAI

BERT provides model evidence. It is not the sole security verdict. The decision engine combines model evidence with independently extracted sender, header, URL and security-rule evidence.

## Evaluation principle

Accuracy, precision, recall, F1, false positives and false negatives must be measured on an explicitly defined unseen test set. Upstream model-card metrics or exploratory evaluation results must not be presented as PhishGuardAI production performance.
