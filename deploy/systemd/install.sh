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

echo "==> Проект: ${PROJECT_DIR}"

mkdir -p "${ENV_DIR}"

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${SCRIPT_DIR}/adparser.env.example" "${ENV_FILE}"
  sed -i "s|^ADPARSER_PROJECT_DIR=.*|ADPARSER_PROJECT_DIR=${PROJECT_DIR}|" "${ENV_FILE}"

  UV_PATH="$(command -v uv || true)"
  if [[ -n "${UV_PATH}" ]]; then
    sed -i "s|^ADPARSER_UV=.*|ADPARSER_UV=${UV_PATH}|" "${ENV_FILE}"
  fi

  chmod 600 "${ENV_FILE}"
  echo "==> Создан ${ENV_FILE} — заполните логин и пароль перед запуском."
else
  echo "==> ${ENV_FILE} уже существует, не перезаписываем."
fi

chmod +x "${SCRIPT_DIR}/run-server.sh" "${SCRIPT_DIR}/run-scheduler.sh"

install_unit() {
  local name="$1"
  local src="${SCRIPT_DIR}/${name}"
  local dst="${SYSTEMD_DIR}/${name}"

  sed \
    -e "s|@PROJECT_DIR@|${PROJECT_DIR}|g" \
    -e "s|@DEPLOY_DIR@|${SCRIPT_DIR}|g" \
    "${src}" > "${dst}"

  echo "==> Установлен ${dst}"
}

install_unit "adparser-server.service"
install_unit "adparser-scheduler.service"

systemctl daemon-reload
systemctl enable adparser-server.service adparser-scheduler.service

echo
echo "Готово. Дальше:"
echo "  1. Отредактируйте ${ENV_FILE} (логин, пароль, пути)"
echo "  2. В каталоге проекта: uv sync && uv run playwright install chromium"
echo "  3. На сервере без GUI: sudo uv run playwright install-deps chromium"
echo "  4. Запуск: sudo systemctl start adparser-server adparser-scheduler"
echo "  5. Статус:  systemctl status adparser-server adparser-scheduler"
echo "  6. Логи:    journalctl -u adparser-server -f"
