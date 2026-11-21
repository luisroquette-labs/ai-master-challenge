#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/check-comments.py --self-test
python3 scripts/check-comments.py
