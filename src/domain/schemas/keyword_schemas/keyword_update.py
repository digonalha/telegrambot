from datetime import datetime
from domain.schemas.keyword_schemas.keyword_base import KeywordBase


class KeywordUpdate(KeywordBase):
    modified_on: datetime
