import ipaddress
import re
from typing import Any, Dict, List, Optional

import requests

_IP_RE = re.compile(r"(?<![\w:])(?:\d{1,3}\.){3}\d{1,3}(?!\w)")


def _valid_public_ip(value: str) -> Optional[str]:
    try:
        ip = ipaddress.ip_address(value)
        if ip.is_global:
            return str(ip)
    except ValueError:
        pass
    return None


def extract_received_chain(headers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    received = []
    for header in headers or []:
        if str(header.get("name", "")).lower() != "received":
            continue
        value = str(header.get("value", ""))
        ips = []
        for raw in _IP_RE.findall(value):
            ip = _valid_public_ip(raw)
            if ip and ip not in ips:
                ips.append(ip)
        received.append({"value": value, "ips": ips})
    return received


def trace_origin(parsed_email: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
    chain = extract_received_chain(parsed_email.get("headers", []))
    candidates = []
    seen = set()
    for item in chain:
        for ip in item["ips"]:
            if ip not in seen:
                seen.add(ip)
                candidates.append(ip)

    origin_ip = candidates[-1] if candidates else None
    location = None
    lookup_error = None
    if origin_ip:
        try:
            response = requests.get(f"https://ipwho.is/{origin_ip}", timeout=timeout)
            if response.ok:
                data = response.json()
                if data.get("success"):
                    location = {
                        "country": data.get("country"),
                        "country_code": data.get("country_code"),
                        "region": data.get("region"),
                        "city": data.get("city"),
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "isp": (data.get("connection") or {}).get("isp"),
                        "organization": (data.get("connection") or {}).get("org"),
                    }
                else:
                    lookup_error = data.get("message") or "IP geolocation lookup failed."
            else:
                lookup_error = f"IP geolocation service returned HTTP {response.status_code}."
        except Exception as exc:
            lookup_error = str(exc)

    return {
        "origin_ip": origin_ip,
        "candidate_ips": candidates,
        "received_hops": chain,
        "location": location,
        "lookup_error": lookup_error,
        "confidence_note": (
            "The displayed IP is the earliest public IP observed in the available Received header chain. "
            "It is not proof of the attacker's physical location."
        ),
    }
