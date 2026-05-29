# Автозапуск через systemd

После перезагрузки сервера поднимаются два сервиса:

| Сервис | Назначение |
|--------|------------|
| `adparser-server` | HTTP-сервер CSV на порту 8000 (`/output.csv`, `/warehouse.csv`) |
| `adparser-scheduler` | Ежедневный парсинг по расписанию (по умолчанию в 02:00) |

Оба сервиса включены в автозагрузку (`WantedBy=multi-user.target`) и перезапускаются при падении.

## Установка на Linux-сервере

```bash
# 1. Клонировать/обновить проект, установить зависимости
cd /opt/adparser   # или ваш путь
uv sync
uv run playwright install chromium
sudo uv run playwright install-deps chromium   # системные библиотеки для Chromium

# 2. Установить unit-файлы systemd
sudo bash deploy/systemd/install.sh

# 3. Заполнить учётные данные
sudo nano /etc/adparser/adparser.env

# 4. Запустить
sudo systemctl start adparser-server adparser-scheduler
```

## Управление

```bash
# Статус
systemctl status adparser-server adparser-scheduler

# Перезапуск после изменения кода или .env
sudo systemctl restart adparser-server adparser-scheduler

# Логи
journalctl -u adparser-server -f
journalctl -u adparser-scheduler -f

# Отключить автозапуск
sudo systemctl disable adparser-server adparser-scheduler
```

## Конфигурация

Файл `/etc/adparser/adparser.env` (шаблон: `adparser.env.example`):

- `ADPARSER_USERNAME` / `ADPARSER_PASSWORD` — логин AutoDealer
- `ADPARSER_SCHEDULE_TIME` — время ежедневного парсинга (`HH:MM`)
- `ADPARSER_WAREHOUSE=1` — дополнительно парсить склад
- `ADPARSER_PORT` — порт CSV-сервера (по умолчанию 8000)

После правки `.env`:

```bash
sudo systemctl restart adparser-server adparser-scheduler
```

## Проверка после перезагрузки

```bash
sudo reboot
# после входа:
systemctl is-active adparser-server adparser-scheduler
curl -I http://127.0.0.1:8000/output.csv
```
