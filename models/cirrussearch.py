from urllib.parse import quote

from pydantic import BaseModel

from models.topic import TopicItem


class Cirrussearch(BaseModel):
    """Prefix and affix are optional attributes

    An exampel use of the affix is to exclude certain words from labels e.g.
    '-inlabel:disorder' removes al items with disorder in the label

    The prefix decides which items to work on and which to exclude based on structured data
    """

    topic: TopicItem
    prefix: str = ""
    affix: str = ""

    @property
    def build_prefix(self):
        """Default to work on scientific articles without the current topic"""
        return f"haswbstatement:P31=Q13442814 -haswbstatement:P921={self.topic.qid}"

    def build_search_expression(self, term: str) -> str:
        """We build a search for the exact term by using quotes around the term"""
        if not term:
            raise ValueError("no term")
        if self.prefix:
            return f'{self.prefix} "{term}" {self.affix}'
        else:
            return f'{self.build_prefix} "{term}" {self.affix}'
