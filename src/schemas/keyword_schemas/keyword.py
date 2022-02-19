from schemas.keyword_schemas.keyword_base import KeywordBase


class Keyword(KeywordBase):
    class Config:
        orm_mode = True
        validate_assignment = True
