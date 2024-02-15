import logging
from pprint import pprint
from typing import Any, List, Optional

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.entities import ItemEntity
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from models.enums import Source, Subgraph
from models.term import Term
from models.topic_curator_base_model import TopicCuratorBaseModel

logger = logging.getLogger(__name__)


class TopicItem(TopicCuratorBaseModel):
    lang: str
    qid: str
    wbi: WikibaseIntegrator = WikibaseIntegrator()
    item: Optional[ItemEntity] = None

    class Config:
        arbitrary_types_allowed = True

    def setup_wbi_user_agent(self):
        wbi_config["USER_AGENT"] = self.user_agent

    def get_item(self):
        if self.item is None:
            logger.debug("getting item")
            self.item = self.wbi.item.get(self.qid)
        else:
            logger.debug("item has already been fetched")

    def setup_wbi_and_get_item(self):
        self.setup_wbi_user_agent()
        self.get_item()

    @property
    def label(self):
        self.setup_wbi_and_get_item()
        try:
            label = self.item.labels.get(language=self.lang).value
        except AttributeError:
            label = "Label missing in this language, please fix"
        return label

    @property
    def aliases(self) -> List[str]:
        self.setup_wbi_and_get_item()
        aliases = self.item.get(self.qid).aliases.get(language=self.lang)
        if aliases is not None:
            aliases = [str(alias) for alias in aliases]
            return aliases
        return []

    @property
    def is_valid(self):
        # logger.debug(f'{self.qid.startswith("Q")} and {self.qid[1:].isdigit()}')
        return self.qid.startswith("Q") and self.qid[1:].isdigit()

    @property
    def url(self):
        return f"https://www.wikidata.org/wiki/{self.qid}"

    @property
    def get_subtopics_as_topic_items(self) -> List[Any]:
        """Get all items that are subclass of this topic as TopicItem

        The only way to do this is via SPARQL"""
        self.setup_wbi_user_agent()
        logger.debug(f"getting subtopics via WDQS for {self.qid}")
        query = f"""
        SELECT ?item
        WHERE {{
				?item wdt:P279 wd:{self.qid}.
        }}
        """
        results = execute_sparql_query(query)
        subtopic_qids = [
            result["item"]["value"].split("/")[-1]
            for result in results["results"]["bindings"]
            if results.get("results") and results.get("results").get("bindings")
        ]
        pprint(subtopic_qids)
        # Propagate WBI because it is maybe slightly faster
        subclass_of_items = [
            TopicItem(qid=item, lang=self.lang, wbi=self.wbi) for item in subtopic_qids
        ]
        return subclass_of_items

    def row_html(self, subgraph: Subgraph) -> str:
        if not subgraph:
            raise ValueError("subgraph missing")
        logger.debug(f"Building row html for {self.qid}")
        match_url = f"/term?lang={self.lang}&qid={self.qid}&subgraph={subgraph.value}"
        from models.cirrussearch import CirrusSearch

        cirrussearch = CirrusSearch(
            topic=self,
            subgraph=subgraph,
            term=Term(string=self.label, source=Source.LABEL),
        )
        return f"""
        <tr>
            <td><a href="{self.url}">{self.label}</a></td>
            <td>{self.description}</td>
            <td><a href"{cirrussearch.cirrussearch_url}">{cirrussearch.cirrussearch_total}</a></td>
            <td><input type="checkbox"></td>
            <td><a href="{match_url}" target="_blank">Match</a></td>
        </tr>
        """

    @property
    def description(self) -> str:
        self.setup_wbi_and_get_item()
        try:
            description = self.item.descriptions.get(language=self.lang).value
        except AttributeError:
            description = "Description missing in this language, please fix"
        return description
