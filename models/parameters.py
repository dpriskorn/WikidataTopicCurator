from typing import List

from pydantic import BaseModel

from models.cirrussearch import Cirrussearch
from models.topic import TopicItem


class Parameters(BaseModel):
    topic: TopicItem
    cirrussearch: Cirrussearch
    limit: int
    search_terms: List[str]
