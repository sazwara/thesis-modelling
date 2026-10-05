#!/bin/zsh
# Run from Terminal with: zsh START_HERE.command
set -eu
cd -- "$(dirname -- "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  print 'Python 3 is missing. Install Python 3.12 from https://www.python.org/downloads/macos/ and try again.'
  exit 1
fi
if ! python3 -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  print 'Please install Python 3.10 or later, preferably Python 3.12, and try again.'
  exit 1
fi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
print 'Open http://localhost:8501 in your browser. Press Control+C here to stop the app.'
.venv/bin/python -m streamlit run app.py
