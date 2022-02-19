from schemas.sale_schemas.sale_base import SaleBase


class Sale(SaleBase):
    id: int

    class Config:
        orm_mode = True
        validate_assignment = True
