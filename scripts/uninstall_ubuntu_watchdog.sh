#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-zokodaily-api}"
SYSTEMD_DIR="/etc/systemd/system"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run this script with sudo/root." >&2
  exit 1
fi

systemctl disable --now "${SERVICE_NAME}-watchdog.timer" 2>/dev/null || true
systemctl disable --now "${SERVICE_NAME}-watchdog.service" 2>/dev/null || true
systemctl disable --now "${SERVICE_NAME}.service" 2>/dev/null || true

rm -f \
  "${SYSTEMD_DIR}/${SERVICE_NAME}.service" \
  "${SYSTEMD_DIR}/${SERVICE_NAME}-watchdog.service" \
  "${SYSTEMD_DIR}/${SERVICE_NAME}-watchdog.timer"

systemctl daemon-reload
echo "Removed ${SERVICE_NAME} service and watchdog timer."
