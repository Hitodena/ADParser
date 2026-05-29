#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Запустите от root: sudo $0" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_DIR="/etc/adparser"
ENV_FILE="${ENV_DIR}/adparser.env"
SYSTEMD_DIR="/etc/systemd/system"

UV_PATH="$(command -v uv || true)"
if [[ -z "${UV_PATH}" ]]; then
  echo "uv не найден в PATH" >&2
  exit 1
fi

echo "==> Проект: ${PROJECT_DIR}"
echo "==> uv:     ${UV_PATH}"

mkdir -p "${ENV_DIR}"

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${SCRIPT_DIR}/adparser.env.example" "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
  echo "==> Создан ${ENV_FILE} — заполните логин и пароль."
else
  echo "==> ${ENV_FILE} уже существует."
fi

install_unit() {
  local name="$1"
  sed \
    -e "s|@PROJECT_DIR@|${PROJECT_DIR}|g" \
    -e "s|@UV@|${UV_PATH}|g" \
    "${SCRIPT_DIR}/${name}" > "${SYSTEMD_DIR}/${name}"
  echo "==> ${SYSTEMD_DIR}/${name}"
}

install_unit "adparser-server.service"
install_unit "adparser.service"

systemctl daemon-reload
systemctl enable adparser-server.service adparser.service

echo
echo "Дальше:"
echo "  1. sudo nano ${ENV_FILE}"
echo "  2. cd ${PROJECT_DIR} && uv sync && uv run playwright install chromium"
echo "  3. sudo systemctl start adparser-server adparser"
