from pydantic import BaseModel
from datetime import datetime


class SaleBase(BaseModel):
    sale_id: int = None
    product_name: str
    product_image_url: str
    old_price: float = None
    price: float
    sale_url: str
    sale_date: datetime
    aggregator_url: str
    store_name: str
