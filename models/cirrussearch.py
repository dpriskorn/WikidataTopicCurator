import logging
from typing import Dict

import yaml
from pydantic import BaseModel

from models.Term import Term
from models.enums import Subgraph
from models.topic import TopicItem

logger = logging.getLogger(__name__)


class Cirrussearch(BaseModel):
    """Prefix and affix are optional attributes

    An exampel use of the affix is to exclude certain words from labels e.g.
    '-inlabel:disorder' removes al items with disorder in the label

    The prefix decides which items to work on and which to exclude based on structured data
    """

    topic: TopicItem
    user_prefix: str = ""
    affix: str = ""
    subgraph: Subgraph
    prefix: Dict[str, str] = dict()

    def read_prefix_from_config(self) -> None:
        with open("config/prefix.yml", "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        # Accessing the 'prefix' section
        self.prefix = data.get("prefix", {})
        for key, value in self.prefix.items():
            logger.debug(f"{key}: {value}")

    @property
    def build_prefix(self):
        """Build prefix based on yaml config and the subgraph enum"""
        if self.user_prefix:
            return self.user_prefix
        else:
            self.read_prefix_from_config()
            # e.g. -> f"haswbstatement:P31=Q13442814 -haswbstatement:P921={self.topic.qid}"
            return self.prefix[self.subgraph.value].format(self.topic.qid)

    def build_search_expression(self, term: Term) -> str:
        """We build a search for the exact term by using quotes around the term
        The term must be in the label and is quoted to be found in full"""
        if not term:
            raise ValueError("no term")
        return f'{self.build_prefix} inlabel:"{term.string}" {self.affix}'
