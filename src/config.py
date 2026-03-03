"""Configuration module for AutoDealer parser."""

from .models import FolderConfig

TIMEOUT = 30

BASE_URL = "https://online.autodealer.ru"
LOGIN_URL = "https://online.autodealer.ru/auth"

BASE_API = "https://online.autodealer.ru/api"
SEARCH_API_URL = BASE_API + "/commonWorks/search"
CURRENT_WORK_URL = BASE_API + "/commonWorks/{id}"

CATALOG_WORKS_URL = "https://online.autodealer.ru/catalogs/works/"
WAREHOUSES_URL = "https://online.autodealer.ru/catalogs/warehouses"


# Folder configurations
FOLDERS = [
    FolderConfig(
        folder_id=8170860, filter_barcode=True, needed_details=True
    ),  # "Комплекс работ"
    FolderConfig(
        folder_id=8104808, filter_barcode=False, needed_details=False
    ),  # "Шиномонтаж"
    FolderConfig(
        folder_id=8108862, filter_barcode=False, needed_details=False
    ),  # "1"
]


def create_search_payload(folder_id: int) -> dict:
    """Create search payload for a specific folder.

    Args:
        folder_id: Folder ID to search in

    Returns:
        Search payload dict
    """
    return {
        "loadedFields": [
            "id",
            "active",
            "aggregation",
            "quickAdd",
            "hasConsumableItems",
            "hasLinked",
            "mark",
            "name",
            "note",
            "barCodes",
            "workCode",
            "priceAmount",
            "currencyCode",
            "coefficient",
            "multiplicity",
            "timeNorm",
            "normHourPrice",
            "totalPriceAmount",
            "category",
            "category.id",
            "category.name",
            "priceType",
            "maxDiscountFactor",
            "executor",
        ],
        "sorts": [
            {
                "direction": "ASC",
                "field": "NAME",
            },
        ],
        "page": 1,
        "pageSize": 200,
        "sortId": None,
        "categories": [],
        "ids": [],
        "marks": [],
        "objectClasses": [],
        "quickAdd": False,
        "text": None,
        "symbol": None,
        "onlyActive": True,
        "includeSubFolders": True,
        "folders": [
            folder_id,
        ],
        "type": "ALL",
        "hasItems": False,
    }


TIME_WHEN_RUN = "02:00"
