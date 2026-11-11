import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from services.feature_extractor import analyze_sender, analyze_urls, extract_features
from services.header_analyzer import analyze_headers


class SecurityAnalysisTests(unittest.TestCase):
    def test_reply_to_mismatch_is_evidence(self):
        result = analyze_sender(
            "Example <alerts@example.com>",
            "support@different.example",
        )
        self.assertTrue(result["reply_to_mismatch"])
        self.assertTrue(any(f["id"] == "reply_to_mismatch" for f in result["findings"]))

    def test_tracking_redirect_uses_embedded_destination(self):
        url = "https://click.redditmail.com/CL0/https:%2F%2Fwww.reddit.com%2Fr%2Fpython%2F"
        result = analyze_urls([url])
        self.assertEqual(result["tracking_wrapper_count"], 1)
        self.assertEqual(result["analyzed_urls"][0]["domain"], "www.reddit.com")
        self.assertEqual(result["findings"], [])

    def test_tracking_wrapper_does_not_flag_encoded_characters(self):
        url = "https://click.example.com/redirect/https:%2F%2Fexample.com%2Faccount%3Fid%3D123%26x%3D456"
        result = analyze_urls([url])
        self.assertFalse(any(f["title"] == "Unusual URL characters" for f in result["findings"]))

    def test_reply_to_mismatch_is_not_decision_warning(self):
        from ai.decision.decision_engine import build_decision
        features = {
            "sender": analyze_sender("Example <alerts@example.com>", "support@different.example"),
            "urls": {"findings": [], "positive_signals": []},
            "headers": {"findings": [], "positive_signals": []},
        }
        decision = build_decision({"phishing_probability": 0.05, "confidence": 0.95}, features)
        self.assertNotIn("Reply-To mismatch", decision["warnings"])

    def test_matching_reply_to_has_no_mismatch(self):
        result = analyze_sender(
            "Example <alerts@example.com>",
            "support@example.com",
        )
        self.assertFalse(result["reply_to_mismatch"])

    def test_url_indicators(self):
        urls = [
            "http://192.168.1.10/login",
            "https://bit.ly/example",
            "https://xn--example-dk9.example/login",
        ]
        result = analyze_urls(urls)
        ids = {finding["id"] for finding in result["findings"]}
        self.assertIn("url_1_http", ids)
        self.assertIn("url_1_ip", ids)
        self.assertIn("url_2_shortened", ids)
        self.assertIn("url_3_punycode", ids)

    def test_long_tracking_url_is_not_warning_by_length_alone(self):
        url = "https://links.example.com/click?token=" + ("a" * 500)
        result = analyze_urls([url])
        self.assertFalse(any(f["title"] == "Unusually long URL" for f in result["findings"]))

    def test_w3_markup_reference_is_not_http_warning(self):
        result = analyze_urls(["http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"])
        self.assertFalse(any(f["title"] == "Insecure HTTP link" for f in result["findings"]))

    def test_header_authentication(self):
        result = analyze_headers({
            "authentication_results": "mx.example; spf=fail; dkim=pass; dmarc=fail",
            "received_spf": "",
            "sender": "alerts@example.com",
            "reply_to": "",
            "return_path": "",
        })
        ids = {finding["id"] for finding in result["findings"]}
        self.assertIn("spf_fail", ids)
        self.assertIn("dmarc_fail", ids)

    def test_features_are_structured(self):
        result = extract_features({
            "id": "test",
            "subject": "Urgent",
            "body": "Please review https://bit.ly/example",
            "sender": "Example <alerts@example.com>",
            "reply_to": "other@example.net",
            "urls": ["https://bit.ly/example"],
            "links": [],
            "authentication_results": "",
            "received_spf": "",
            "return_path": "",
        })
        self.assertIn("sender", result)
        self.assertIn("urls", result)
        self.assertIn("headers", result)
        self.assertIsInstance(result["sender"]["findings"], list)


if __name__ == "__main__":
    unittest.main()


def test_displayed_link_domain_mismatch_is_high_risk():
    from backend.services.feature_extractor import analyze_urls
    result = analyze_urls(
        ["https://evil.example/login"],
        [{"visible_text": "https://accounts.example.com/security", "actual_url": "https://evil.example/login"}],
    )
    assert any(item["id"] == "link_1_display_mismatch" and item["severity"] == "high" for item in result["findings"])
