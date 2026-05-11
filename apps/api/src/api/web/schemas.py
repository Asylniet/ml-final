from typing import Generic

from pydantic import BaseModel, Field

from core.utils.types import T


class PaginatedResponseSchema(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class CommonFiltersSchema(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, gt=0, le=100, description="Items per page")


class AddressSchema(BaseModel):
    locality: str
    street: str
    building_number: str
    apartment_number: str | None = None
