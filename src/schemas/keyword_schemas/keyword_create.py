from datetime import datetime
from schemas.keyword_schemas.keyword_base import KeywordBase


class KeywordCreate(KeywordBase):
    created_on: datetime
    modified_on: datetime
