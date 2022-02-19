from datetime import datetime
from schemas.sale_schemas.sale_base import SaleBase


class SaleCreate(SaleBase):
    created_on: datetime

