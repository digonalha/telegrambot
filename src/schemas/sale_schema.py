from pydantic import BaseModel
from datetime import datetime


class SaleBase(BaseModel):
    sale_id: int
    product_name: str
    product_image_url: str
    old_price: float = None
    price: float
    sale_url: str
    sale_date: datetime
    aggregator_url: str


class SaleCreate(SaleBase):
    created_on: datetime


class Sale(SaleBase):
    id: int

    class Config:
        orm_mode = True
        validate_assignment = True
