from sqlalchemy import Column, BigInteger, String, DateTime, Numeric
from repositories.database.config import base


class TrackedSale(base):
    __tablename__ = "tracked_sale"

    sale_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    product_name = Column(String, nullable=False)
    product_image_url = Column(String, nullable=True)
    old_price = Column(Numeric(10, 2), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    sale_url = Column(String, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    aggregator_url = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
