# Testing Structure

## Unit
`tests/unit/` covers deterministic decision-engine behavior and security scoring rules.

## Integration
`tests/integration/` covers database persistence, user ownership, metadata minimization, and repository behavior.

## API
`tests/api/` covers history endpoints, Google identity validation, and configuration/security contracts.

## AI
`tests/ai/` contains fixture evaluation and metric-related test utilities.

## End-to-end
`tests/end_to_end/` contains pipeline smoke/contract coverage. A full browser E2E run still requires a locally installed browser automation runtime and a configured Google test account; it is not claimed as completed by the Python suite alone.
