from sqlalchemy import Column, BigInteger, String, DateTime, Numeric
from src.repositories.database.config import base


class Sale(base):
    __tablename__ = "sale"

    sale_id = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    product_name = Column(String, nullable=False)
    product_image_url = Column(String, nullable=True)
    price = Column(Numeric, nullable=False)
    sale_url = Column(String, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    created_on = Column(DateTime, nullable=False)
    modified_on = Column(DateTime, nullable=False)
