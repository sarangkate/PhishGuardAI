import re
from pathlib import PurePath
from typing import Any, Dict, List

HIGH_RISK_EXTENSIONS = {
    ".exe", ".scr", ".com", ".bat", ".cmd", ".ps1", ".vbs", ".vbe",
    ".js", ".jse", ".wsf", ".wsh", ".msi", ".msp", ".hta", ".lnk",
}
MEDIUM_RISK_EXTENSIONS = {
    ".iso", ".img", ".jar", ".reg", ".chm", ".docm", ".xlsm", ".pptm",
}
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".tar", ".gz"}


def _finding(finding_id: str, title: str, severity: str, evidence: str) -> Dict[str, str]:
    return {
        "id": finding_id,
        "category": "attachment",
        "title": title,
        "severity": severity,
        "evidence": evidence,
        "source": "attachment_analysis",
    }


def analyze_attachments(attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
    findings: List[Dict[str, str]] = []
    positives: List[Dict[str, str]] = []
    analyzed = []

    for index, item in enumerate(attachments or [], start=1):
        filename = str(item.get("filename", "") or "").strip()
        mime_type = str(item.get("mime_type", "") or "").lower()
        lower = filename.lower()
        suffixes = [suffix.lower() for suffix in PurePath(lower).suffixes]
        final_suffix = suffixes[-1] if suffixes else ""
        indicators = []

        if final_suffix in HIGH_RISK_EXTENSIONS:
            indicators.append("Executable/script attachment type")
            findings.append(_finding(
                f"attachment_{index}_executable", "Executable or script attachment", "critical",
                f"The attachment '{filename or 'unnamed'}' uses the high-risk extension {final_suffix}.",
            ))
        elif final_suffix in MEDIUM_RISK_EXTENSIONS:
            indicators.append("Potentially risky attachment type")
            findings.append(_finding(
                f"attachment_{index}_risky_type", "Potentially risky attachment type", "high",
                f"The attachment '{filename or 'unnamed'}' uses the extension {final_suffix}.",
            ))

        if len(suffixes) >= 2 and final_suffix in HIGH_RISK_EXTENSIONS:
            visible_previous = suffixes[-2]
            if visible_previous in {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png", ".txt"}:
                indicators.append("Double extension may disguise executable")
                findings.append(_finding(
                    f"attachment_{index}_double_extension", "Disguised double-extension attachment", "critical",
                    f"The filename '{filename}' appears to combine a document/image extension with executable content.",
                ))

        if final_suffix in ARCHIVE_EXTENSIONS:
            indicators.append("Archive attachment")

        if mime_type in {"application/x-msdownload", "application/x-dosexec"} and final_suffix not in HIGH_RISK_EXTENSIONS:
            findings.append(_finding(
                f"attachment_{index}_mime_executable", "Executable attachment MIME type", "critical",
                f"The attachment '{filename or 'unnamed'}' is labeled with an executable MIME type.",
            ))

        analyzed.append({
            "filename": filename,
            "mime_type": mime_type,
            "size": item.get("size"),
            "attachment_id_present": bool(item.get("attachment_id")),
            "indicators": indicators,
        })

    if attachments and not findings:
        positives.append({
            "type": "attachment",
            "title": "No high-risk attachment type detected",
            "evidence": f"Reviewed metadata for {len(attachments)} attachment(s) without downloading their contents.",
            "source": "attachment_analysis",
        })

    return {
        "attachment_count": len(attachments or []),
        "analyzed_attachments": analyzed,
        "findings": findings,
        "positive_signals": positives,
    }
