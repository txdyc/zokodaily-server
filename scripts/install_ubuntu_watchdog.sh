#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVICE_NAME="${SERVICE_NAME:-zokodaily-api}"
RUN_USER="${RUN_USER:-${SUDO_USER:-$USER}}"
RUN_GROUP="${RUN_GROUP:-$(id -gn "${RUN_USER}")}"
FLASK_PORT="${FLASK_PORT:-8000}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:${FLASK_PORT}/api/health}"
ENV_FILE="${ENV_FILE:-${SERVER_ROOT}/.env.production}"
SYSTEMD_DIR="/etc/systemd/system"

API_SERVICE_PATH="${SYSTEMD_DIR}/${SERVICE_NAME}.service"
WATCHDOG_SERVICE_PATH="${SYSTEMD_DIR}/${SERVICE_NAME}-watchdog.service"
WATCHDOG_TIMER_PATH="${SYSTEMD_DIR}/${SERVICE_NAME}-watchdog.timer"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run this script with sudo/root." >&2
  exit 1
fi

chmod +x "${SCRIPT_DIR}/run_api_service.sh" "${SCRIPT_DIR}/check_api_heartbeat.sh"

cat > "${API_SERVICE_PATH}" <<EOF
[Unit]
Description=Zokodaily Flask API Service
After=network.target

[Service]
Type=simple
User=${RUN_USER}
Group=${RUN_GROUP}
WorkingDirectory=${SERVER_ROOT}
Environment=APP_ENV=production
Environment=FLASK_PORT=${FLASK_PORT}
EnvironmentFile=-${ENV_FILE}
ExecStart=${SCRIPT_DIR}/run_api_service.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat > "${WATCHDOG_SERVICE_PATH}" <<EOF
[Unit]
Description=Zokodaily API heartbeat watchdog
After=network.target ${SERVICE_NAME}.service

[Service]
Type=oneshot
Environment=SERVICE_NAME=${SERVICE_NAME}.service
Environment=HEALTH_URL=${HEALTH_URL}
ExecStart=${SCRIPT_DIR}/check_api_heartbeat.sh
EOF

cat > "${WATCHDOG_TIMER_PATH}" <<EOF
[Unit]
Description=Run Zokodaily API heartbeat watchdog every minute

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Unit=${SERVICE_NAME}-watchdog.service
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"
systemctl enable --now "${SERVICE_NAME}-watchdog.timer"

echo "Installed systemd service and watchdog timer:"
echo "  ${API_SERVICE_PATH}"
echo "  ${WATCHDOG_SERVICE_PATH}"
echo "  ${WATCHDOG_TIMER_PATH}"
echo
echo "Health check URL: ${HEALTH_URL}"
echo "Use 'systemctl status ${SERVICE_NAME}.service' to verify."
echo "Use 'systemctl list-timers | grep ${SERVICE_NAME}-watchdog' to verify timer."
