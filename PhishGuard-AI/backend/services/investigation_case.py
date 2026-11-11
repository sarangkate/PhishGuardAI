"""Build an evidence-linked investigation case from an analyzed email.

This module deliberately distinguishes observed evidence from derived relationships.
It never claims that an observed IP is the attacker's physical location.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _domain_from_address(value: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+)", str(value or ""))
    return match.group(1).lower().rstrip(".") if match else ""


def _evidence_item(item: Dict[str, Any], index: int) -> Dict[str, Any]:
    evidence_id = str(item.get("id") or f"E-{index:03d}")
    return {
        "evidence_id": evidence_id,
        "category": str(item.get("category") or "security"),
        "title": str(item.get("title") or "Security finding"),
        "severity": str(item.get("severity") or "info"),
        "observed_value": item.get("evidence") or item.get("message") or item.get("reason") or "",
        "source": str(item.get("source") or "analysis_pipeline"),
    }


def build_investigation_case(email: Dict[str, Any], analysis: Dict[str, Any], origin: Dict[str, Any]) -> Dict[str, Any]:
    risk = analysis.get("risk_analysis", {}) or {}
    features = analysis.get("features", {}) or {}
    evidence_raw = risk.get("evidence", []) or []
    evidence: List[Dict[str, Any]] = []
    for index, item in enumerate(evidence_raw, start=1):
        if isinstance(item, dict):
            evidence.append(_evidence_item(item, index))

    case_id = f"PG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{_sha256_json({'message_id': email.get('id'), 'subject': email.get('subject', '')})[:10].upper()}"

    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    node_ids = set()

    def add_node(node_id: str, node_type: str, label: str, value: str = "", confidence: str = "observed"):
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append({"id": node_id, "type": node_type, "label": label, "value": value, "confidence": confidence})

    def add_edge(source: str, target: str, relationship: str, evidence_ids: List[str] | None = None):
        if source not in node_ids or target not in node_ids:
            return
        edges.append({"source": source, "target": target, "relationship": relationship, "evidence_ids": evidence_ids or [], "confidence": "derived"})

    message_id = str(email.get("id") or "unknown")
    add_node("email", "email", "Email", message_id)

    sender = str(email.get("sender") or "")
    sender_domain = _domain_from_address(sender)
    if sender:
        add_node("sender", "sender", "Sender", sender)
        add_edge("email", "sender", "sent_by")
    if sender_domain:
        add_node("sender-domain", "domain", "Sender domain", sender_domain)
        add_edge("sender", "sender-domain", "uses_domain")

    reply_domain = _domain_from_address(str(email.get("reply_to") or ""))
    if reply_domain:
        add_node("reply-domain", "domain", "Reply-To domain", reply_domain)
        if sender_domain:
            add_edge("sender-domain", "reply-domain", "reply_to_relationship")

    urls = (features.get("urls", {}) or {}).get("urls", []) or (features.get("urls", {}) or {}).get("items", []) or []
    first_url_node = None
    for index, item in enumerate(urls[:20], start=1):
        if not isinstance(item, dict):
            url = str(item)
        else:
            url = str(item.get("actual_url") or item.get("url") or "")
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not host:
            continue
        url_node = f"url-{index}"
        domain_node = f"url-domain-{index}"
        add_node(url_node, "url", "URL", url)
        add_node(domain_node, "domain", "URL domain", host)
        add_edge("email", url_node, "contains_url")
        add_edge(url_node, domain_node, "targets_domain")
        if first_url_node is None:
            first_url_node = url_node

    origin_ip = str(origin.get("origin_ip") or "")
    if origin_ip:
        add_node("origin-ip", "ip", "Earliest observed public IP", origin_ip, "observed")
        add_edge("email", "origin-ip", "observed_in_received_chain")
        location = origin.get("location") or {}
        organization = str(location.get("organization") or location.get("isp") or "")
        if organization:
            add_node("origin-org", "infrastructure", "IP organization", organization)
            add_edge("origin-ip", "origin-org", "associated_with")

    auth = (features.get("headers", {}) or {}).get("authentication", {}) or {}
    for method in ("spf", "dkim", "dmarc"):
        value = str(auth.get(method) or "none").lower()
        add_node(f"auth-{method}", "authentication", method.upper(), value)
        add_edge("email", f"auth-{method}", "authentication_result")

    # Reuse finding IDs as links into the graph where possible.
    for item in evidence:
        title = item["title"].lower()
        ids = [item["evidence_id"]]
        if "url" in title and first_url_node:
            edges.append({"source": first_url_node, "target": "email", "relationship": "supported_by_finding", "evidence_ids": ids, "confidence": "observed"})
        elif "sender" in title and sender_domain:
            edges.append({"source": "sender-domain", "target": "email", "relationship": "supported_by_finding", "evidence_ids": ids, "confidence": "observed"})

    manifest = {
        "case_id": case_id,
        "message_id": message_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "evidence": evidence,
        "nodes": nodes,
        "edges": edges,
        "classification": risk.get("classification"),
        "risk_score": risk.get("risk_score"),
    }
    evidence_hash = _sha256_json(manifest)

    return {
        "case_id": case_id,
        "created_at": manifest["created_at"],
        "classification": risk.get("classification"),
        "risk_score": risk.get("risk_score"),
        "trust_score": risk.get("trust_score"),
        "evidence": evidence,
        "nodes": nodes,
        "edges": edges,
        "evidence_manifest_sha256": evidence_hash,
        "integrity_note": "SHA-256 fingerprints the generated evidence manifest. It supports later integrity comparison; it does not by itself prove authenticity or chain of custody.",
    }
