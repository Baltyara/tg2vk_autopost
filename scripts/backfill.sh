#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"
python3 -m tg2vk backfill "$@"

