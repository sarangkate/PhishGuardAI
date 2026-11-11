from backend.services.investigation_case import build_investigation_case


def test_investigation_case_links_evidence_and_is_deterministically_structured():
    email = {"id": "m-123", "sender": 'Security <alert@example.com>', "reply_to": "reply@other.example"}
    analysis = {
        "features": {
            "urls": {"urls": [{"actual_url": "https://example.net/login"}]},
            "headers": {"authentication": {"spf": "pass", "dkim": "fail", "dmarc": "fail"}},
        },
        "risk_analysis": {
            "classification": "Phishing",
            "risk_score": 82,
            "trust_score": 18,
            "evidence": [{"id": "url_1", "category": "url", "title": "Suspicious URL", "severity": "high", "evidence": "example.net", "source": "url_analysis"}],
        },
    }
    origin = {"origin_ip": "8.8.8.8", "location": {"organization": "Example ISP"}}
    case = build_investigation_case(email, analysis, origin)
    assert case["case_id"].startswith("PG-")
    assert case["evidence_manifest_sha256"] and len(case["evidence_manifest_sha256"]) == 64
    assert any(n["id"] == "origin-ip" for n in case["nodes"])
    assert any(e["evidence_ids"] == ["url_1"] for e in case["edges"])
