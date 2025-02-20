import logging
from json import JSONDecodeError
from typing import Any

import requests
from pydantic import ConfigDict
from requests import Session

from models.exceptions import QleverError
from models.topic_curator_base_model import TopicCuratorBaseModel

logger = logging.getLogger(__name__)


class QleverIntegrator(TopicCuratorBaseModel):
    endpoint: str = "https://qlever.cs.uni-freiburg.de/api/wikidata"
    session: Session = requests.session()
    model_config = ConfigDict(  # dead:disable
        arbitrary_types_allowed=True, extra="forbid"
    )
    action: str = "json_export"

    def execute_qlever_sparql_query(
        self,
        query: str,
    ) -> dict[str, Any]:
        if self.action not in ["tsv_export", "json_export"]:
            raise QleverError(f"Action {self.action} is not supported")
        params = {
            "query": query,
            "action": "json_export",
        }
        try:
            response = self.session.get(
                self.endpoint,
                params=params,
                headers=self.headers,
            )
        except requests.exceptions.ConnectionError:
            raise QleverError(
                "ConnectionError"
            ) from requests.exceptions.ConnectionError
        if len(response.text) > 0:
            return response.json()
        else:
            # Try again
            try:
                response = self.session.get(
                    self.endpoint,
                    params=params,
                    headers=self.headers,
                )
            except requests.exceptions.ConnectionError:
                raise QleverError(
                    "ConnectionError"
                ) from requests.exceptions.ConnectionError
            try:
                return response.json()
            except JSONDecodeError:
                # todo tell the user to refresh because of an intermittent error that persists
                raise QleverError("Got no data from QLever endpoint") from None
