# ruff: noqa: B019
# ruff: noqa: S608

import logging
from functools import lru_cache

from flatten_json import flatten  # type:ignore
from wikibaseintegrator.wbi_config import config as wbi_config  # type:ignore
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
    items: list[SparqlItem] = []
    item_count: int = 0
    has_been_run: bool = False

    def __hash__(self):
        return hash(self.wdqs_query_string)

    def __set_user_agent__(self):
        wbi_config["USER_AGENT"] = self.user_agent

    @property
    def cirrussearch(self) -> CirrusSearch:
        return self.parameters.get_cirrussearch(term=self.term)

    @property
    def calculated_limit(self) -> int:
        return self.parameters.limit - self.item_count

    def __run_and_parse_results__(self) -> list[SparqlItem]:
        # console.print(self.results)
        items = []
        for item_json in self.__execute__()["results"]["bindings"]:
            # logging.debug(f"item_json:{item_json}")
            item_json = flatten(item_json)
            logging.debug(f"flattened item_json:{item_json}")
            item = SparqlItem(
                item=item_json.get("item_value", ""),
                item_label=item_json.get("itemLabel_value", ""),
                instance_of_label=item_json.get("instance_ofLabel_value", ""),
                publication_label=item_json.get("publicationLabel_value", ""),
                doi=item_json.get("doi_id_value", ""),
                raw_full_resources=item_json.get("full_resources_value", ""),
            )
            # pprint(item.model_dump())
            items.append(item)
        return items

    def __execute__(self):
        if not self.wdqs_query_string:
            raise ValueError("no query string")
        return execute_sparql_query(self.wdqs_query_string)

    @lru_cache(maxsize=128)
    def run_and_get_items(self) -> list[SparqlItem]:
        """Do everything needed to get the results"""
        self.__set_user_agent__()
        self.has_been_run = True
        return self.__run_and_parse_results__()

    @property
    def generate_279_minus_lines(self):
        lines = []
        for levels in range(2, 15):
            subpath = "wdt:P921"
            path = subpath
            # We start at -1 because of the start path
            # e.g. number=2 => "wdt:P921/wdt:P921"
            for _ in range(1, levels):
                path += f"/{subpath}"
            lines.append(f"\t\tMINUS {{?item {path} wd:{self.parameters.topic.qid}. }}")
        return "\n".join(lines)

    @property
    def wdqs_query_string(self) -> str:
        # This query uses https://www.w3.org/TR/sparql11-property-paths/ to
        # find subjects that are subclass of one another up to 3 hops away
        # This query also uses the https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI
        # which has a hardcoded limit of 10,000 items so you will never get more matches than that
        logger.debug(
            f"using cirrussearch_string: '{self.cirrussearch.cirrussearch_string}"
        )
        return f"""
            #{self.user_agent}
            SELECT DISTINCT ?item ?itemLabel ?instance_ofLabel
            ?publicationLabel ?doi_id
            (GROUP_CONCAT(DISTINCT ?full_resource; separator=",")
             as ?full_resources)
            WHERE {{
              hint:Query hint:optimizer "None".
              BIND(STR('{self.cirrussearch.cirrussearch_string}') as ?search_string)
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                mwapi:srsearch ?search_string.
                ?title wikibase:apiOutput mwapi:title.
              }}
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item wdt:P31 ?instance_of.
              optional{{
              ?item wdt:P1433 ?publication.
                }}
              optional{{
              ?item wdt:P356 ?doi_id.
                }}
              optional{{
              ?item wdt:P953 ?full_resource.
              }}
              # Remove items that have a main subject that is subclass of this topic from the results
              # Do it for 15 levels because cell types has such a deep hierarchy
              {self.generate_279_minus_lines}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{self.lang}". }}
            }}
            GROUP BY ?item ?itemLabel ?instance_ofLabel ?publicationLabel ?doi_id
            LIMIT {self.calculated_limit}
        """

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

    @lru_cache
    def row_html(self, count: int) -> str:
        total = self.cirrussearch.cirrussearch_total()
        logger.info(
            f"cs total cache: {self.cirrussearch.cirrussearch_total.cache_info()}"
        )
        return f"""
        <tr>
            <td>{count}</td>
            <td>
                <a href="{self.cirrussearch.cirrussearch_url}">{self.term.string}</a>
            </td>
            <td>
                {len(self.items)} included / <a href="{self.cirrussearch.cirrussearch_url}">{total} total</a>
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
