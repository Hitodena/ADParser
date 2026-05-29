# Автозапуск через systemd

Два сервиса — те же команды, что в README:

| Сервис | Команда |
|--------|---------|
| `adparser-server` | `uv run -m src.server` |
| `adparser` | `uv run python main.py -u … -p … -o output.csv --scheduled --time "02:00"` |

Парсер сам держит расписание через `--scheduled` (библиотека `schedule` в `main.py`).

## Установка

```bash
cd /opt/adparser
uv sync
uv run playwright install chromium
sudo uv run playwright install-deps chromium

sudo bash deploy/systemd/install.sh
sudo nano /etc/adparser/adparser.env
sudo systemctl start adparser-server adparser
```

## Конфиг `/etc/adparser/adparser.env`

- `ADPARSER_USERNAME` / `ADPARSER_PASSWORD` — логин AutoDealer
- `ADPARSER_SCHEDULE_TIME` — время парсинга (`02:00` по умолчанию)
- `ADPARSER_EXTRA_ARGS` — доп. флаги CLI, напр. `-w --headless`

## Управление

```bash
systemctl status adparser-server adparser
journalctl -u adparser -f
sudo systemctl restart adparser-server adparser
```
