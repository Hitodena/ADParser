"""Data models for AutoDealer parser."""

from typing import Any

from pydantic import BaseModel, Field


class FolderConfig(BaseModel):
    """Configuration for a folder to parse."""

    folder_id: int
    filter_barcode: (
        bool  # True = only services with barcodes, False = all services
    )
    needed_details: bool = True  # True = fetch detailed info (items/works)


class BarcodeDTO(BaseModel):
    """Barcode model."""

    id: int
    number: str
    type: str
    active: bool


class MarkDTO(BaseModel):
    """Mark/model of car."""

    id: int
    name: str


class MarkListItemDTO(BaseModel):
    """Mark list item (can be without id)."""

    id: int | None = None
    name: str = ""


class WorkListItem(BaseModel):
    """Work list item from /api/commonWorks/folders."""

    model_config = {"strict": False}

    id: int
    name: str
    barcodes: list[BarcodeDTO] = Field(
        default_factory=list, validation_alias="barCodes"
    )
    totalPriceAmount: float | None = None
    mark: MarkListItemDTO = Field(
        default_factory=MarkListItemDTO, validation_alias="mark"
    )
    active: bool = True


class ManufacturerDTO(BaseModel):
    """Manufacturer of nomenclature."""

    id: int
    name: str
    active: bool = True


class NomenclaturePriceDTO(BaseModel):
    """Price of nomenclature."""

    id: int
    priceAmount: float
    currencyCode: str
    defaultPrice: bool = True
    name: str


class NomenclatureDTO(BaseModel):
    """Nomenclature (goods/item) model."""

    id: int
    name: str
    manufacturer: ManufacturerDTO | None = None
    manufacturerNumbers: list[BarcodeDTO] = Field(
        default_factory=list, validation_alias="manufacturerNumbers"
    )
    prices: list[NomenclaturePriceDTO] = Field(
        default_factory=list, validation_alias="prices"
    )
    active: bool = True


class FormItemDTO(BaseModel):
    """Form item (contains nomenclature/goods) in work detail."""

    id: int
    nomenclature: NomenclatureDTO
    quantity: float
    priceAmount: float
    calcPriceAmount: float
    active: bool = True


class WorkDTO(BaseModel):
    """Work operation in work detail."""

    id: int
    name: str
    priceAmount: float
    calcPriceAmount: float
    active: bool = True


class WorkDetail(BaseModel):
    """Detailed work from /api/commonWorks/{id}."""

    id: int
    name: str
    barcodes: list[BarcodeDTO] = Field(
        default_factory=list, validation_alias="barCodes"
    )
    totalPriceAmount: float
    formItems: list[FormItemDTO] = Field(
        default_factory=list, validation_alias="formItems"
    )
    works: list[WorkDTO] = Field(
        default_factory=list, validation_alias="works"
    )
    active: bool = True


class WorksListResponse(BaseModel):
    """Response from /api/commonWorks/folders."""

    entityList: list[WorkListItem]
    info: dict[str, Any]
