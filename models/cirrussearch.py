# ruff: noqa: B019

import logging
from functools import lru_cache
from urllib.parse import quote

import requests
import yaml
from pydantic import BaseModel

from models.enums import Subgraph
from models.term import Term
from models.topic_item import TopicItem

logger = logging.getLogger(__name__)


class CirrusSearch(BaseModel):
    """Prefix and affix are optional attributes

    An example use of the affix is to exclude certain words from labels e.g.
    '-inlabel:disorder' removes al items with disorder in the label

    The prefix decides which items to work on and which to exclude based on structured data
    """

    topic: TopicItem
    term: Term
    subgraph: Subgraph
    user_prefix: str = ""
    affix: str = ""
    prefix_from_config: dict[str, str] = {}

    def __hash__(self):
        return hash(self.cirrussearch_string)

    def read_prefix_from_config(self) -> None:
        with open("config/prefix.yml") as file:
            data = yaml.safe_load(file)
        # Accessing the 'prefix' section
        self.prefix_from_config = data.get("prefix", {})
        # for key, value in self.prefix_from_config.items():
        #     logger.debug(f"{key}: {value}")

    @property
    def build_prefix(self):
        """Build prefix based on yaml config and the subgraph enum"""
        if self.user_prefix:
            return self.user_prefix
        else:
            self.read_prefix_from_config()
            # e.g. -> f"haswbstatement:P31=Q13442814 -haswbstatement:P921={self.topic.qid}"
            return self.prefix_from_config[self.subgraph.value].format(self.topic.qid)

    @property
    def cirrussearch_string(self) -> str:
        """We build a search for the exact term by using quotes around the term
        The term must be in the label and is quoted to be found in full"""
        return f'{self.build_prefix} inlabel:"{self.term.string}" {self.affix}'

    @lru_cache
    def cirrussearch_total(self) -> int:
        logger.debug("Getting CirrusSearch total")
        if not self.term.string:
            # Return 0 early if string is empty
            logger.debug("Empty term string, returning 0.")
            return 0
        base_url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "formatversion": 2,
            "srsearch": str(self.cirrussearch_string),
            "srlimit": 1,
            "srprop": "size",
        }

        response = requests.get(base_url, params=params)  # type: ignore

        if response.status_code == 200:
            data = response.json()
            # pprint(data)
            total_hits = data.get("query", {}).get("searchinfo", {}).get("totalhits", 0)
            logger.debug(f"CirrusSearch total: {total_hits}")
            # format like gs total
            return int(total_hits)
        else:
            logger.error(f"Unable to fetch data. Status code: {response.status_code}")
            return 0

    @property
    def cirrussearch_url(self) -> str:
        return (
            f"https://www.wikidata.org/w/index.php?search="
            f"{quote(self.cirrussearch_string)}"
            f"&title=Special%3ASearch&profile=advanced&fulltext=1&ns0=1"
        )
