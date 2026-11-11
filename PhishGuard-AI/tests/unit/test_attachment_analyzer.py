from backend.services.attachment_analyzer import analyze_attachments


def test_double_extension_executable_is_critical():
    result = analyze_attachments([{"filename": "invoice.pdf.exe", "mime_type": "application/octet-stream"}])
    ids = {item["id"] for item in result["findings"]}
    assert "attachment_1_executable" in ids
    assert "attachment_1_double_extension" in ids


def test_normal_pdf_is_not_flagged():
    result = analyze_attachments([{"filename": "invoice.pdf", "mime_type": "application/pdf"}])
    assert result["findings"] == []
