# AutoDealer Parser

AutoDealer service catalog parser.

## Install

```bash
# Install uv (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

## Usage

### One-time run

```bash
uv run python main.py -u <username> -p <password> -o output.csv
```

### Scheduled run

```bash
uv run python main.py -u <username> -p <password> -o output.csv --scheduled --time "02:00"
```

### Warehouse parser

```bash
# Parse services only (default)
uv run python main.py -u <username> -p <password> -o output.csv

# Parse services AND warehouse (runs both sequentially)
uv run python main.py -u <username> -p <password> -o output.csv -w

# Parse warehouse only is NOT supported - use -w to run BOTH
```

## Arguments

| Argument | Short | Description | Default |
| ---------- | ------- | ------------- | --------- |
| `--username` | `-u` | Login | required |
| `--password` | `-p` | Password | required |
| `--output` | `-o` | CSV path for services | `output.csv` |
| `--output-warehouse` | `-ow` | CSV path for warehouse | `warehouse.csv` |
| `--scheduled` | `-s` | Run daily at specified time | no |
| `--time` | `-t` | Time for scheduled run (HH:MM) | `02:00` |
| `--warehouse` | `-w` | Also parse warehouse after services | no |

## CSV Columns

- `service_id` — Service ID
- `service_name` — Service name
- `barcode` — Barcode
- `price_total` — Total price
- `works_names` — Work names (JSON array)
- `works_prices` — Work prices (JSON array)
- `works_totals` — Work totals (JSON array)
- `item_names` — Item names (JSON array)
- `item_articles` — Articles (JSON array)
- `item_brands` — Brands (JSON array)
- `item_quantities` — Quantities (JSON array)
- `item_prices` — Item prices (JSON array)
- `item_totals` — Item totals (JSON array)

### Warehouse CSV Columns

- `name` — Наименование в чеке
- `manufacturer` — Производитель
- `unit_of_measure` — Единица измерения
- `manufacturer_number` — Артикул производителя
- `quantity` — Количество
- `selling_price` — Цена продажи
- `purchase_price` — Цена прихода
- `max_discount` — Максимальная скидка

## Project Structure

```plain
.
├── main.py           # Entry point
├── src/
│   ├── parser.py     # Orchestrator
│   ├── client client
│  .py     # API ├── auth.py       # Authentication
│   ├── session.py    # Session capture
│   ├── models.py     # Pydantic models
│   ├── config.py     # Configuration
│   ├── csv_writer.py # CSV writer
│   └── browser.py    # BrowserManager
└── output.csv        # Result
```
