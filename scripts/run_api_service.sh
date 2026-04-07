#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export APP_ENV="${APP_ENV:-production}"
export FLASK_HOST="${FLASK_HOST:-0.0.0.0}"
export FLASK_PORT="${FLASK_PORT:-8000}"

find_python() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    printf '%s\n' "${PYTHON_BIN}"
    return
  fi

  local candidates=(
    "${SERVER_ROOT}/.venv/bin/python"
    "${SERVER_ROOT}/.conda/bin/python"
    "$(command -v python3 2>/dev/null || true)"
    "$(command -v python 2>/dev/null || true)"
  )
  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -n "${candidate}" && -x "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  return 1
}

PYTHON_EXE="$(find_python)" || {
  echo "No suitable Python interpreter found." >&2
  exit 1
}

cd "${SERVER_ROOT}"
exec "${PYTHON_EXE}" api_server.py
