import logging
from pprint import pprint
from typing import List, Dict
from urllib.parse import quote

import requests
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from models.Term import Term
from models.google_scholar import GoogleScholarSearch
from models.item import Item
from models.parameters import Parameters
from models.topic_curator_base_model import TopicCuratorBaseModel
from models.value import Value

logger = logging.getLogger(__name__)


class Query(TopicCuratorBaseModel):
    """We need a search_string and the parameters"""

    term: Term
    parameters: Parameters
    results: Dict = {}
    wdqs_query_string: str = ""
    items: List[Item] = list()
    lang: str = "en"
    item_count: int = 0
    has_been_run: bool = False

    def __parse_results__(self) -> None:
        # console.print(self.results)
        for item_json in self.results["results"]["bindings"]:
            # logging.debug(f"item_json:{item_json}")
            item = Item(
                item=item_json["item"],
                itemLabel=item_json.get("itemLabel", Value()),
                instance_ofLabel=item_json.get("instance_ofLabel", Value()),
                publicationLabel=item_json.get("publicationLabel", Value()),
                doi_id=item_json.get("doi_id", Value()),
                full_resource=item_json.get("full_resource", Value()),
            )
            # pprint(item.model_dump())
            self.items.append(item)

    def __execute__(self):
        self.results = execute_sparql_query(self.wdqs_query_string)

    def start(self):
        """Do everything needed to get the results"""
        self.__prepare_and_build_query__()
        self.__execute__()
        self.__parse_results__()
        self.has_been_run = True

    @property
    def cirrussearch_string(self):
        return self.parameters.cirrussearch.build_search_expression(term=self.term)

    def __prepare_and_build_query__(
        self,
    ):
        logger.debug(f"using cirrussearch_string: '{self.cirrussearch_string}")
        self.__build_query__()

    @property
    def get_everywhere_google_results(self) -> int:
        gs = GoogleScholarSearch(term=self.term)
        return gs.everywhere_total_results

    @property
    def get_in_title_google_results(self) -> int:
        gs = GoogleScholarSearch(term=self.term)
        return gs.in_title_total_results

    @property
    def get_in_title_google_url(self) -> str:
        gs = GoogleScholarSearch(term=self.term)
        return gs.in_title_url()

    @property
    def get_everywhere_google_url(self) -> str:
        gs = GoogleScholarSearch(term=self.term)
        return gs.everywhere_url()

    @staticmethod
    def formatted_google_results(number: int) -> str:
        formatted_number = "{:,}".format(number)
        return formatted_number

    @property
    def cirrussearch_total(self) -> int:
        logger.debug("Getting CirrusSearch total")
        base_url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "formatversion": 2,
            "srsearch": self.cirrussearch_string,
            "srlimit": 1,
            "srprop": "size",
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            pprint(data)
            total_hits = data.get("query", {}).get("searchinfo", {}).get("totalhits", 0)
            logger.debug(f"cs total: {total_hits}")
            # format like gs total
            return int(total_hits)
        else:
            logger.error(f"Unable to fetch data. Status code: {response.status_code}")
            return 0

    def row_html(self, count: int) -> str:
        return f"""
        <tr>
            <td>{count}</td>
            <td>
                <a href="{self.cirrussearch_url}">{self.term.string}</a>
            </td>
            <td>
                {len(self.items)} included / <a href="{self.cirrussearch_url}">{self.cirrussearch_total} total</a>
            </td>
            <td>
                {self.has_been_run}
            </td>
            <td>
            In title: <a href="{self.get_in_title_google_url}">
                {self.formatted_google_results(number=self.get_in_title_google_results)}</a> 
            (everywhere: <a href="{self.get_in_title_google_url}">
                    {self.formatted_google_results(number=self.get_everywhere_google_results)}</a>)</td>
        </tr>
        """

    @property
    def cirrussearch_url(self) -> str:
        return (
            f"https://www.wikidata.org/w/index.php?search="
            f"{quote(self.parameters.cirrussearch.build_search_expression(term=self.term))}"
            f"&title=Special%3ASearch&profile=advanced&fulltext=1&ns0=1"
        )
