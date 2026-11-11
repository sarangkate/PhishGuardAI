from pathlib import Path


def test_e2e_plan_covers_complete_flow():
    text = Path("docs/E2E_TEST_PLAN.md").read_text()
    required = ["GOOGLE AUTHENTICATION", "GMAIL AUTHORIZATION", "BERT", "DECISION ENGINE", "AWARENESS"]
    for item in required:
        assert item in text
