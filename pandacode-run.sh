#!/usr/bin/env bash
# pandacode-preview: http://127.0.0.1:8765
set -eu
cd "$(dirname "$0")"
if command -v python >/dev/null 2>&1; then
  exec python -B cinema.py --no-browser
fi
exec python3 -B cinema.py --no-browser
