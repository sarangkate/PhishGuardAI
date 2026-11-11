#!/usr/bin/env bash
set -e
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
export PYTHONPATH="$(pwd)"
python -m ai.scripts.download_model
