import logging
from typing import List, Dict

from pydantic import BaseModel
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from models.google_scholar import GoogleScholarSearch
from models.item import Item
from models.parameters import Parameters
from models.value import Value
from urllib.parse import quote

logger = logging.getLogger(__name__)


class Query(BaseModel):
    """We need a search_string and the parameters"""

    term: str
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

    def __prepare_and_build_query__(self):
        pass

    @property
    def get_total_google_results(self) -> int:
        gs = GoogleScholarSearch(search_string=self.term)
        return gs.total_results()

    @property
    def get_google_url(self) -> str:
        gs = GoogleScholarSearch(search_string=self.term)
        return gs.en_url()

    @property
    def formatted_google_results(self):
        formatted_number = '{:,}'.format(self.get_total_google_results)
        return formatted_number

    def row_html(self, count: int) -> str:
        return f"""
        <tr>
            <td>{count}</td>
            <td>
                <a href="{self.cirrussearch_url}">{self.term}</a>
            </td>
            <td>
                {len(self.items)}
            </td>
            <td>
                {self.has_been_run}
            </td>
            <td><a href="{self.get_google_url}">{self.formatted_google_results}</a></td>
        </tr>
        """

    @property
    def cirrussearch_url(self) -> str:
        return (
            f"https://www.wikidata.org/w/index.php?search="
            f"{quote(self.parameters.cirrussearch.build_search_expression(term=self.term))}"
            f"&title=Special%3ASearch&profile=advanced&fulltext=1&ns0=1"
        )
