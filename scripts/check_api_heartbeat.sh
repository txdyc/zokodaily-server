#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-zokodaily-api.service}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/api/health}"
CURL_BIN="${CURL_BIN:-$(command -v curl 2>/dev/null || true)}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-10}"
LOG_TAG="${LOG_TAG:-zokodaily-api-watchdog}"

if [[ -z "${CURL_BIN}" ]]; then
  echo "curl is required but was not found." >&2
  exit 1
fi

status_code="$("${CURL_BIN}" \
  --silent \
  --show-error \
  --output /dev/null \
  --write-out "%{http_code}" \
  --max-time "${TIMEOUT_SECONDS}" \
  "${HEALTH_URL}" || true)"

if [[ "${status_code}" == "200" ]]; then
  exit 0
fi

echo "[${LOG_TAG}] Health check failed for ${HEALTH_URL} with status '${status_code}', restarting ${SERVICE_NAME}."
systemctl restart "${SERVICE_NAME}"
