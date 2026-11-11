# Performance Optimization

## Implemented optimizations

- BERT is loaded lazily and cached as a single in-process model instance.
- BERT inference uses `torch.inference_mode()` rather than gradient tracking.
- Tokenization uses dynamic padding instead of padding every message to the full 512-token length.
- The frontend uses request timeouts and avoids duplicate client-side history persistence.
- Gmail analysis is performed once per analysis request and the parsed email is reused for persistence.

## Privacy-aware caching rule

Raw email content must not be placed in a long-lived application cache. Any future cache must use bounded metadata or a short-lived request scope.

## Measurement

Production performance should be measured with real deployment telemetry (request latency, BERT inference latency, error rate, and concurrent-user load). No performance numbers are claimed until measured.
