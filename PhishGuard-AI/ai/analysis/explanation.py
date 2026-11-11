from typing import Any, Dict, List


def explain(decision: Dict[str, Any]) -> Dict[str, Any]:
    evidence: List[Dict[str, Any]] = decision.get("evidence", [])
    explanation_items = []
    for item in evidence:
        explanation_items.append({
            "title": item.get("title"),
            "severity": item.get("severity"),
            "evidence": item.get("evidence"),
            "source": item.get("source"),
        })

    if not explanation_items:
        summary = "No rule-based warning evidence was detected."
    else:
        summary = (
            f"The email received a {decision.get('classification')} assessment based on "
            f"{len(explanation_items)} evidence item(s) from the security analyzers."
        )

    return {"summary": summary, "items": explanation_items}
