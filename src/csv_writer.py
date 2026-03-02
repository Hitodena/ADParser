"""CSV writer module for AutoDealer parser."""

import csv
import json
from pathlib import Path
from typing import Any

from .models import WorkDetail, WorkListItem


def write_to_csv(
    works_list: list[WorkListItem],
    work_details: list[WorkDetail],
    output_path: str,
) -> None:
    """Write parsed data to CSV file.

    Args:
        works_list: List of work list items from API
        work_details: List of detailed work information
        output_path: Path to output CSV file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    details_map: dict[int, WorkDetail] = {d.id: d for d in work_details}

    fieldnames = [
        "service_id",
        "service_name",
        "barcode",
        "price_total",
        "works_names",
        "works_prices",
        "works_totals",
        "item_names",
        "item_articles",
        "item_brands",
        "item_quantities",
        "item_prices",
        "item_totals",
    ]

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for work in works_list:
            detail = details_map.get(work.id)

            barcode = ""
            if work.barcodes:
                barcode = work.barcodes[0].number

            works_names: list[str] = []
            works_prices: list[str] = []
            works_totals: list[str] = []
            if detail and detail.works:
                for w in detail.works:
                    works_names.append(w.name)
                    works_prices.append(str(w.priceAmount))
                    works_totals.append(str(w.calcPriceAmount))

            item_names: list[str] = []
            item_articles: list[str] = []
            item_brands: list[str] = []
            item_quantities: list[str] = []
            item_prices: list[str] = []
            item_totals: list[str] = []
            if detail and detail.formItems:
                for item in detail.formItems:
                    item_names.append(
                        item.nomenclature.name if item.nomenclature else ""
                    )
                    article = ""
                    if (
                        item.nomenclature
                        and item.nomenclature.manufacturerNumbers
                    ):
                        article = item.nomenclature.manufacturerNumbers[
                            0
                        ].number
                    item_articles.append(article)
                    brand = ""
                    if item.nomenclature and item.nomenclature.manufacturer:
                        brand = item.nomenclature.manufacturer.name
                    item_brands.append(brand)
                    item_quantities.append(str(item.quantity))
                    item_prices.append(str(item.priceAmount))
                    item_totals.append(str(item.calcPriceAmount))

            row: dict[str, Any] = {
                "service_id": work.id,
                "service_name": work.name,
                "barcode": barcode,
                "price_total": work.totalPriceAmount,
                "works_names": json.dumps(works_names, ensure_ascii=False),
                "works_prices": json.dumps(works_prices, ensure_ascii=False),
                "works_totals": json.dumps(works_totals, ensure_ascii=False),
                "item_names": json.dumps(item_names, ensure_ascii=False),
                "item_articles": json.dumps(item_articles, ensure_ascii=False),
                "item_brands": json.dumps(item_brands, ensure_ascii=False),
                "item_quantities": json.dumps(
                    item_quantities, ensure_ascii=False
                ),
                "item_prices": json.dumps(item_prices, ensure_ascii=False),
                "item_totals": json.dumps(item_totals, ensure_ascii=False),
            }

            writer.writerow(row)
