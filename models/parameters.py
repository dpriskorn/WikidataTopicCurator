from pydantic import BaseModel

from models.cirrussearch import Cirrussearch
from models.terms import Terms
from models.topic import TopicItem


class Parameters(BaseModel):
    topic: TopicItem
    cirrussearch: Cirrussearch
    limit: int
    terms: Terms
