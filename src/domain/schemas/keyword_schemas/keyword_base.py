from pydantic import BaseModel


class KeywordBase(BaseModel):
    user_id: int
    keyword: str
    max_price: int = None
