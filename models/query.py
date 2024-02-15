import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type:ignore

from models.cirrussearch import CirrusSearch
from models.google_scholar import GoogleScholarSearch
from models.sparqlitem import SparqlItem
from models.term import Term
from models.topic_curator_base_model import TopicCuratorBaseModel
from models.topicparameters import TopicParameters

logger = logging.getLogger(__name__)


class Query(TopicCuratorBaseModel):
    """We need a search_string and the parameters"""

    lang: str
    term: Term
    parameters: TopicParameters
    results: dict = {}
    wdqs_query_string: str = ""
    items: list[SparqlItem] = []
    item_count: int = 0
    has_been_run: bool = False

    @property
    def cirrussearch(self) -> CirrusSearch:
        return self.parameters.get_cirrussearch(term=self.term)

    @property
    def calculated_limit(self) -> int:
        return self.parameters.limit - self.item_count

    def __parse_results__(self) -> None:
        # console.print(self.results)
        for item_json in self.results["results"]["bindings"]:
            # logging.debug(f"item_json:{item_json}")
            item = SparqlItem(
                item=item_json["item"],
                item_label=item_json.get("itemLabel").get("value"),
                instance_of_label=item_json.get("instance_ofLabel").get("value"),
                publication_label=item_json.get("publicationLabel").get("value"),
                doi=item_json.get("doi_id").get("value"),
                raw_full_resources=item_json.get("full_resources").get("value"),
            )
            # pprint(item.model_dump())
            self.items.append(item)

    def __execute__(self):
        if not self.wdqs_query_string:
            raise ValueError("no query string")
        self.results = execute_sparql_query(self.wdqs_query_string)

    def start(self):
        """Do everything needed to get the results"""
        self.__prepare_and_build_query__()
        self.__execute__()
        self.__parse_results__()
        self.has_been_run = True

    def __prepare_and_build_query__(
        self,
    ):
        logger.debug(
            f"using cirrussearch_string: '{self.cirrussearch.cirrussearch_string}"
        )
        self.__build_query__()

    # @property
    # def get_everywhere_google_results(self) -> int:
    #     gs = GoogleScholarSearch(term=self.term)
    #     return gs.everywhere_total_results
    #
    # @property
    # def get_in_title_google_results(self) -> int:
    #     gs = GoogleScholarSearch(term=self.term)
    #     return gs.in_title_total_results

    @property
    def get_in_title_google_url(self) -> str:
        gs = GoogleScholarSearch(term=self.term)
        return gs.in_title_url()

    @property
    def get_everywhere_google_url(self) -> str:
        gs = GoogleScholarSearch(term=self.term)
        return gs.everywhere_url()

    # @staticmethod
    # def formatted_google_results(number: int) -> str:
    #     formatted_number = f"{number:,}"
    #     return formatted_number

    def row_html(self, count: int) -> str:
        return f"""
        <tr>
            <td>{count}</td>
            <td>
                <a href="{self.cirrussearch.cirrussearch_url}">{self.term.string}</a>
            </td>
            <td>
                {len(self.items)} included / <a href="{self.cirrussearch.cirrussearch_url}">{self.cirrussearch.cirrussearch_total} total</a>
            </td>
            <td>
                {self.has_been_run}
            </td>
            <td>
            <a href="{self.get_in_title_google_url}">
                in title only</a> | <a href="{self.get_everywhere_google_url}">
                    everywhere (fulltext search)</a>)</td>
        </tr>
        """
