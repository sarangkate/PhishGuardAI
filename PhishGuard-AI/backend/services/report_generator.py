from io import BytesIO
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def _safe(value):
    if value is None or value == "":
        return "—"
    return escape(str(value))


def _paragraph(text, style):
    return Paragraph(_safe(text), style)


def build_forensic_pdf(email, analysis, origin):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="PhishGuardAI Forensic Email Report",
        author="PhishGuardAI",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Evidence", parent=styles["BodyText"], fontSize=9, leading=12, leftIndent=8))

    story = [
        Paragraph("PhishGuardAI", styles["TitleCenter"]),
        Paragraph("Forensic Email Security Report", styles["Heading2"]),
        Spacer(1, 4),
        _paragraph(f"Generated: {datetime.now(timezone.utc).isoformat()}", styles["Small"]),
        Spacer(1, 10),
    ]

    risk = analysis.get("risk_analysis", {}) or {}
    summary = [
        ["Classification", _safe(risk.get("classification"))],
        ["Risk score", _safe(risk.get("risk_score"))],
        ["Trust score", _safe(risk.get("trust_score"))],
        ["Model confidence", _safe(risk.get("model_confidence"))],
        ["Sender", _safe(email.get("sender"))],
        ["Subject", _safe(email.get("subject"))],
        ["Date", _safe(email.get("date"))],
        ["Message ID", _safe(email.get("id"))],
    ]
    table = Table(summary, colWidths=[42 * mm, 138 * mm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eef2f7")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [Paragraph("1. Executive Summary", styles["Section"]), table]

    story += [Paragraph("2. Authentication & Header Evidence", styles["Section"])]
    auth = (analysis.get("features", {}) or {}).get("headers", {}) or {}
    auth_state = auth.get("authentication") or {}
    auth_table = Table([
        ["Signal", "Result"],
        ["SPF", _safe(str(auth_state.get("spf", "none")).upper())],
        ["DKIM", _safe(str(auth_state.get("dkim", "none")).upper())],
        ["DMARC", _safe(str(auth_state.get("dmarc", "none")).upper())],
        ["Header findings", _safe("; ".join(auth.get("warnings", []) or auth.get("warning_signs", []) or []))],
    ], colWidths=[45*mm,135*mm])
    auth_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.4,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#eef2f7")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(auth_table)

    story += [Paragraph("3. Origin Trace", styles["Section"])]
    loc = origin.get("location") or {}
    origin_rows = [
        ["Observed origin IP", _safe(origin.get("origin_ip"))],
        ["Country", _safe(loc.get("country"))],
        ["Region", _safe(loc.get("region"))],
        ["City", _safe(loc.get("city"))],
        ["ISP / Organization", _safe(loc.get("isp") or loc.get("organization"))],
    ]
    ot = Table(origin_rows, colWidths=[45*mm,135*mm])
    ot.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.4,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#eef2f7")),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9)]))
    story += [ot, Spacer(1,5), _paragraph(origin.get("confidence_note"), styles["Small"])]

    story += [Paragraph("4. Detected Evidence", styles["Section"])]
    evidence = risk.get("evidence", []) or []
    if evidence:
        for item in evidence:
            if isinstance(item, dict):
                text = f"{item.get('severity','').upper()}: {item.get('message') or item.get('reason') or item}"
            else:
                text = str(item)
            story.append(Paragraph("• " + _safe(text), styles["Evidence"]))
    else:
        story.append(_paragraph("No concrete warning evidence was recorded by the analysis pipeline.", styles["BodyText"]))

    story += [Paragraph("5. Warning Signs & Recommendations", styles["Section"])]
    warnings = risk.get("warnings", []) or []
    for item in warnings:
        story.append(Paragraph("• " + _safe(item), styles["Evidence"]))
    rec = risk.get("recommendation", {}) or {}
    actions = rec.get("actions", []) or []
    if actions:
        story.append(Spacer(1,4))
        story.append(Paragraph("Recommended actions:", styles["BodyText"]))
        for item in actions:
            story.append(Paragraph("• " + _safe(item), styles["Evidence"]))

    case = analysis.get("investigation_case", {}) or {}
    story += [Paragraph("5A. Investigation Case", styles["Section"])]
    case_table = Table([
        ["Case ID", _safe(case.get("case_id"))],
        ["Evidence items", _safe(len(case.get("evidence", []) or []))],
        ["Graph nodes", _safe(len(case.get("nodes", []) or []))],
        ["Graph relationships", _safe(len(case.get("edges", []) or []))],
        ["Evidence manifest SHA-256", _safe(case.get("evidence_manifest_sha256"))],
    ], colWidths=[55*mm,125*mm])
    case_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.4,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#eef2f7")),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.5),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(case_table)
    story.append(_paragraph(case.get("integrity_note"), styles["Small"]))
    story += [Paragraph("5B. Attack / Infrastructure Chain", styles["Section"])]
    for edge in (case.get("edges", []) or [])[:40]:
        story.append(Paragraph("• " + _safe(f"{edge.get('source')} → {edge.get('target')} | {edge.get('relationship')} | Evidence: {', '.join(edge.get('evidence_ids', []))}"), styles["Evidence"]))
    story += [PageBreak(), Paragraph("6. URL & Sender Analysis", styles["Section"])]
    features = analysis.get("features", {}) or {}
    sender = features.get("sender", {}) or {}
    urls = features.get("urls", {}) or {}
    story.append(_paragraph("Sender findings: " + "; ".join(sender.get("warnings", []) or sender.get("warning_signs", []) or []), styles["BodyText"]))
    story.append(Spacer(1,5))
    url_items = urls.get("urls", []) or urls.get("items", []) or []
    if url_items:
        for item in url_items[:30]:
            if isinstance(item, dict):
                story.append(Paragraph("• " + _safe(item.get("url") or item.get("actual_url") or item), styles["Evidence"]))
            else:
                story.append(Paragraph("• " + _safe(item), styles["Evidence"]))
    else:
        story.append(_paragraph("No extracted URLs were recorded.", styles["BodyText"]))

    story += [Spacer(1,12), Paragraph("Report note", styles["Section"]), _paragraph(
        "This report summarizes automated security analysis. IP geolocation is approximate and should not be treated as proof of an attacker's physical identity or location. Preserve the original message and headers when conducting formal investigations.",
        styles["Small"])]

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
