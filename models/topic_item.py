import logging
import sys
from pprint import pprint
from typing import Any

import requests
from pydantic import ConfigDict
from requests import Session
from wikibaseintegrator import WikibaseIntegrator  # type:ignore
from wikibaseintegrator.entities import ItemEntity  # type:ignore
from wikibaseintegrator.wbi_config import config as wbi_config  # type:ignore
from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type:ignore

from models.enums import Source, Subgraph
from models.exceptions import WikibaseRestApiError
from models.term import Term
from models.wikibase_rest import WikibaseRestApi, WikibaseRestItem

logger = logging.getLogger(__name__)


class TopicItem(WikibaseRestItem):
    """This is our Topic item with methods adapted to this specific tool"""

    session: Session = requests.session()
    model_config = ConfigDict(  # dead:disable
        arbitrary_types_allowed=True, extra="forbid"
    )

    def setup_wbi_user_agent(self):
        wbi_config["USER_AGENT"] = self.user_agent

    # @property
    # def label(self):
    #     api = WikibaseRestApi(qid=self.qid, lang=self.lang, session=self.session)
    #     label = api.get_label
    #     if label is None or not label:
    #         label = "Label missing in this language, please fix"
    #     return label
    #
    # @property
    # def description(self) -> str:
    #     api = WikibaseRestApi(qid=self.qid, lang=self.lang, session=self.session)
    #     description = api.get_description
    #     if description is None or not description:
    #         description = "Description missing in this language, please fix"
    #     return description
    #
    # @property
    # def aliases(self) -> list[str]:
    #     api = WikibaseRestApi(qid=self.qid, lang=self.lang, session=self.session)
    #     return api.get_aliases

    @property
    def is_valid(self):
        # logger.debug(f'{self.qid.startswith("Q")} and {self.qid[1:].isdigit()}')
        return self.qid.startswith("Q") and self.qid[1:].isdigit()

    @property
    def url(self):
        return f"https://www.wikidata.org/wiki/{self.qid}"

    @property
    def has_subtopic(self) -> bool:
        self.setup_wbi_user_agent()
        logger.debug(f"checking if any subtopics via WDQS for {self.qid}")
        query = f"""
        SELECT (count(?item) as ?count)
        WHERE {{
                ?item wdt:P279 wd:{self.qid}.
        }}
        """
        results = execute_sparql_query(query=query, endpoint="")
        count = int(results["results"]["bindings"][0]["count"]["value"])
        logger.debug(f"subtopics found: {count}")
        boolean = bool(count)
        logger.debug(f"subtopics found: {boolean}")
        return boolean
        #     return True
        # else:
        #     return False

    @property
    async def get_subtopics_as_topic_items(self) -> list[Any]:
        """Get all items that are subclass of this topic as TopicItem
        The only way to do this is via SPARQL"""
        self.setup_wbi_user_agent()
        # self.get_item()
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
        # qids = ["Q123", "Q456", "Q7839"]  # Example list of IDs
        api = WikibaseRestApi(qids=subtopic_qids, lang=self.lang)
        items = await api.fetch_all_items()

        for item in items:
            print(item.model_dump())
            sys.exit()
        return items

        # subclass_of_items = [
        #     TopicItem(qid=item, lang=self.lang, session=self.session) for item in subtopic_qids
        # ]
        # return subclass_of_items

    def row_html(self, subgraph: Subgraph) -> str:
        """This function uses the async fetched values"""
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
    def get_label(self) -> str:
        """This is slow"""
        url = f"{self.base_url}/entities/items/{self.qid}/labels"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get(self.lang, "")
        else:
            raise WikibaseRestApiError(f"got {response.status_code} from Wikibase")

    @property
    def get_aliases(self) -> list[str]:
        """This is slow"""
        url = f"{self.base_url}/entities/items/{self.qid}/aliases"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get(self.lang, [])
        else:
            raise WikibaseRestApiError(f"got {response.status_code} from Wikibase")

    # @property
    # def get_description(self) -> str:
    #     url = f"{self.endpoint_url}/entities/items/{self.qid}/descriptions"
    #     response = requests.get(url, headers=self.headers)
    #     if response.status_code == 200:
    #         return response.json().get(self.lang, "")
    #     else:
    #         raise WikibaseRestApiError(f"got {response.status_code} from Wikibase")
    #
