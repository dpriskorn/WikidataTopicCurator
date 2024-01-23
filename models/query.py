import logging
from pprint import pprint
from typing import List, Dict

from pydantic import BaseModel
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from models.item import Item
from models.value import Value

logger = logging.getLogger(__name__)


class Query(BaseModel):
    """We need a search_string and a main_subject_item"""

    search_string: str
    main_subject_item: str
    results: Dict = {}
    query_string: str = ""
    items: List[Item] = list()
    lang: str = "en"

    def __parse_results__(self) -> None:
        # console.print(self.results)
        for item_json in self.results["results"]["bindings"]:
            logging.debug(f"item_json:{item_json}")
            item = Item(
                item=item_json["item"],
                itemLabel=item_json.get("itemLabel", Value()),
                instance_ofLabel=item_json.get("instance_ofLabel", Value()),
                publicationLabel=item_json.get("publicationLabel", Value()),
                doi_id=item_json.get("doi_id", Value()),
                full_resource=item_json.get("full_resource", Value()),
            )
            pprint(item.model_dump())
            self.items.append(item)

    def __strip_bad_chars__(self):
        # Note this has to match the cleaning done in the sparql query
        # We lowercase and remove common symbols
        # We replace like this to save CPU cycles see
        # https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string
        self.search_string = (
            self.search_string
            # Needed for matching backslashes e.g. "Dmel\CG5330" on Q29717230
            .replace("\\", "\\\\")
            # Needed for when labels contain apostrophe
            .replace("'", "\\'")
            .replace(",", "")
            .replace(":", "")
            .replace(";", "")
            .replace("(", "")
            .replace(")", "")
            .replace("[", "")
            .replace("]", "")
        )

    def __execute__(self):
        self.results = execute_sparql_query(self.query_string)

    def start(self):
        """Do everything needed to get the results"""
        self.__strip_bad_chars__()
        self.__prepare_and_build_query__()
        self.__execute__()
        self.__parse_results__()

    def __prepare_and_build_query__(self):
        pass
