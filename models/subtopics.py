import logging
import time
from functools import lru_cache
from pprint import pprint
from typing import Any

from flatten_json import flatten_json
from pydantic import BaseModel, Field

from models.exceptions import QleverError
from models.qlever import QleverIntegrator
from models.topic_item import TopicItem
from models.wikibase_rest.item import WikibaseRestItem

logger = logging.getLogger(__name__)


class Subtopics(BaseModel):
    subtopics: list[WikibaseRestItem] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    qid: str
    lang: str

    @property
    def subtopics_json(self) -> list[Any]:
        """Exports the data in row_html as a JSON dictionary."""
        data = []
        for topic in self.subtopics:
            data.append(topic.model_dump(exclude={"aliases", "base_url"}))
        return data

    def fetch_subtopics(self) -> None:
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
        self.data = qi.execute_qlever_sparql_query(query=query)
        # pprint(self.data)
        # exit()
        status = self.data.get("status")
        if status == "ERROR":
            raise QleverError(self.data.get("exception"))
        # Calculate execution time
        execution_time = time.time() - start_time
        logger.info(f"SPARQL query: {execution_time} seconds")

    def parse_into_topic_items(self) -> None:
        # print(self.data)
        # exit()
        bindings = self.data["results"]["bindings"]
        for result in bindings:
            data = flatten_json(result)
            # pprint(data)
            # exit()
            self.subtopics.append(
                WikibaseRestItem(
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
        logger.info(f"Got {len(self.subtopics)} subtopics")

    def fetch_and_parse(self):
        self.fetch_subtopics()
        self.parse_into_topic_items()
