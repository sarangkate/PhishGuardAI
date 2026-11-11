$ErrorActionPreference = "Stop"

Write-Host "Installing PhishGuardAI AI dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

Write-Host "Downloading/caching the configured phishing BERT model..."
$env:PYTHONPATH = (Get-Location).Path
python -m ai.scripts.download_model

Write-Host "AI environment setup completed."
