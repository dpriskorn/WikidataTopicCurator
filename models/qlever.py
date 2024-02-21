from typing import Any

import requests
from pydantic import BaseModel, ConfigDict
from requests import Session

from models.exceptions import QleverError
from models.topic_curator_base_model import TopicCuratorBaseModel


class ActionError(BaseException):
    pass


class QleverIntegrator(TopicCuratorBaseModel):
    endpoint: str = "https://qlever.cs.uni-freiburg.de/api/wikidata"
    session: Session = requests.session()
    model_config = ConfigDict(  # dead:disable
        arbitrary_types_allowed=True, extra="forbid"
    )

    def execute_sparql_query(
        self, query: str, action: str = "json_export"
    ) -> dict[str, Any]:
        if action not in ["tsv_export", "json_export"]:
            raise ActionError(f"Action {action} is not supported")
        params = {
            "query": query,
            "action": "json_export",
        }
        try:
            response = self.session.get(
                "https://qlever.cs.uni-freiburg.de/api/wikidata",
                params=params,
                headers=self.headers,
            )
        except requests.exceptions.ConnectionError:
            raise QleverError(
                "ConnectionError"
            ) from requests.exceptions.ConnectionError
        return response.json()
