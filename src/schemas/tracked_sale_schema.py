from pydantic import BaseModel
from datetime import datetime


class TrackedSaleBase(BaseModel):
    sale_id: int
    product_name: str
    product_image_url: str
    old_price: float = None
    price: float
    sale_url: str
    sale_date: datetime
    aggregator_url: str


class TrackedSaleCreate(TrackedSaleBase):
    created_on: datetime


class TrackedSale(TrackedSaleBase):
    class Config:
        orm_mode = True
        validate_assignment = True
