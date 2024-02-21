# ruff: noqa: B019

import logging
import time
from functools import lru_cache
from typing import Any

import requests
from flatten_json import flatten_json  # type:ignore
from pydantic import ConfigDict
from requests import Session

from models.enums import Subgraph
from models.exceptions import QleverError, WikibaseRestApiError
from models.qlever import QleverIntegrator
from models.wikibase_rest.item import WikibaseRestItem

logger = logging.getLogger(__name__)


class TopicItem(WikibaseRestItem):
    """This is our Topic item with methods adapted to this specific tool"""

    session: Session = requests.session()
    model_config = ConfigDict(  # dead:disable
        arbitrary_types_allowed=True, extra="forbid"
    )

    def __eq__(self, other):
        return self.qid == other.qid

    def __hash__(self):
        return hash(self.qid)

    @property
    def is_valid(self):
        # logger.debug(f'{self.qid.startswith("Q")} and {self.qid[1:].isdigit()}')
        return self.qid.startswith("Q") and self.qid[1:].isdigit()

    @property
    def url(self):
        return f"https://www.wikidata.org/wiki/{self.qid}"

    @lru_cache
    def get_subtopics_as_topic_items(self) -> list[Any]:
        """Get all items that are subclass of this topic as TopicItem
        The only way to do this is via SPARQL"""
        logger.debug("get_subtopics_as_topic_items: running")
        # Start measuring execution time
        start_time = time.time()
        # self.setup_wbi_user_agent()
        # self.get_item()
        logger.debug(f"getting subtopics via QLever for {self.qid}")
        query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>

        SELECT ?item ?itemLabel ?itemDescription
        WHERE {{
          ?item wdt:P279 wd:{self.qid}. # Replace QID_VALUE with the QID you want to use
          OPTIONAL {{
            ?item rdfs:label ?itemLabel.
            FILTER(LANG(?itemLabel) = "{self.lang}")
          }}
          OPTIONAL {{
            ?item schema:description ?itemDescription.
            FILTER(LANG(?itemDescription) = "{self.lang}")
          }}
        }}
        """
        qi = QleverIntegrator()
        results = qi.execute_qlever_sparql_query(query=query)
        status = results.get("status")
        if status == "ERROR":
            raise QleverError(results.get("exception"))
        # pprint(results)
        # exit()
        bindings = results["results"]["bindings"]
        subtopics = []
        for result in bindings:
            data = flatten_json(result)
            # pprint(data)
            # exit()
            subtopics.append(
                TopicItem(
                    lang=self.lang,
                    qid=data.get("item_value").split("/")[-1],
                    label=data.get(
                        "itemLabel_value", "Label missing in this language, please fix"
                    ),
                    description=data.get(
                        "itemDescription_value",
                        "Description missing in this language, please fix",
                    ),
                )
            )
        #     = [
        #     result["item"]["value"].split("/")[-1]
        #     for result in results["results"]["bindings"]
        #     if results.get("results") and results.get("results").get("bindings")
        # ]
        logger.info(f"Got {len(subtopics)} subtopics")
        # pprint(subtopic_qids)
        # Calculate execution time
        execution_time = time.time() - start_time
        logger.info(
            f"SPARQL query and object conversion time: {execution_time} seconds"
        )
        return subtopics

    @lru_cache
    def row_html(self, subgraph: Subgraph) -> str:
        """This function uses the async fetched values"""
        if not subgraph:
            raise ValueError("subgraph missing")
        # logger.debug(f"Building row html for {self.qid}")
        match_url = f"/term?lang={self.lang}&qid={self.qid}&subgraph={subgraph.value}"
        # from models.cirrussearch import CirrusSearch
        #
        # cirrussearch = CirrusSearch(
        #     topic=self,
        #     subgraph=subgraph,
        #     term=Term(string=self.label, source=Source.LABEL),
        # )
        # return f"""
        # <tr>
        #     <td><a href="{self.url}">{self.label}</a></td>
        #     <td>{self.description}</td>
        #     <td><a href"{cirrussearch.cirrussearch_url}">{cirrussearch.cirrussearch_total}</a></td>
        #     <td><input type="checkbox"></td>
        #     <td><a href="{match_url}" target="_blank">Match</a></td>
        # </tr>
        # """
        return f"""
        <tr>
            <td><a href="{self.url}">{self.label}</a></td>
            <td>{self.description}</td>
            <td>Disabled for performance reasons</td>
            <td><input type="checkbox"></td>
            <td><a href="{match_url}" target="_blank">Match</a></td>
        </tr>
        """

    @lru_cache
    def get_label(self) -> str:
        """This is slow"""
        url = f"{self.base_url}/entities/items/{self.qid}/labels"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get(self.lang, "")
        else:
            raise WikibaseRestApiError(f"got {response.status_code} from Wikibase")

    @lru_cache
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
