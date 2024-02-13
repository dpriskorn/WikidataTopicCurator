from pydantic import BaseModel

from models.cirrussearch import CirrusSearch
from models.enums import Subgraph
from models.term import Term
from models.terms import Terms
from models.topic_item import TopicItem


class TopicParameters(BaseModel):
    topic: TopicItem
    limit: int
    terms: Terms
    subgraph: Subgraph
    user_prefix: str = ""
    affix: str = ""

    def get_cirrussearch(self, term: Term) -> CirrusSearch:
        if not term:
            raise ValueError("no term")
        return CirrusSearch(
            topic=self.topic,
            term=term,
            user_prefix=self.user_prefix,
            affix=self.affix,
            subgraph=self.subgraph,
        )
