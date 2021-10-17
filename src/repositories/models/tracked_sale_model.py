from sqlalchemy import Column, BigInteger, String, DateTime
from src.repositories.database.config import base


class TrackedSale(base):
    __tablename__ = "tracked_sale"

    sale_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    product_name = Column(String, nullable=False)
    product_image_url = Column(String, nullable=True)
    price = Column(String, nullable=False)
    sale_url = Column(String, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    aggregator_url = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
