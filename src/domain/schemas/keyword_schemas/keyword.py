from domain.schemas.keyword_schemas.keyword_base import KeywordBase


class Keyword(KeywordBase):
    id: int

    class Config:
        orm_mode = True
        validate_assignment = True
