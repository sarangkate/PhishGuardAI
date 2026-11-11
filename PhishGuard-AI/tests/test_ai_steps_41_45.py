from pathlib import Path

def test_step_40_loading_component_exists():
    text=Path("frontend/src/components/AnalysisLoading.jsx").read_text(); assert "EMAIL" in text and "SECURITY CHECK" in text and "RESULT" in text

def test_step_41_no_raw_exception_details():
    text=Path("backend/routes/analysis.py").read_text(); assert "detail=str(error)" not in text

def test_step_42_dashboard_exists():
    text=Path("frontend/src/App.jsx").read_text(); assert "Dashboard" in text and "Emails analyzed" in text and "history.filter" in text

def test_step_43_history_is_server_side_and_metadata_only():
    text=Path("frontend/src/App.jsx").read_text(); assert "/api/history" in text and "risk_score" in text and "phishguard_analysis_history" not in text

def test_step_44_awareness_topics_exist():
    text=Path("frontend/src/App.jsx").read_text();
    for topic in ["Phishing","Sender verification","Link safety","Urgency tactics","Credential theft","Impersonation","Attachment safety","Independent verification"]: assert topic in text

def test_step_45_settings_sections_exist():
    text=Path("frontend/src/App.jsx").read_text();
    for section in ["Account","Privacy","Security","About","Disconnect account"]: assert section in text
