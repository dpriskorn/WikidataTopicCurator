from pydantic import BaseModel


class TopicCuratorBaseModel(BaseModel):
    base_url: str = "https://www.wikidata.org/w/rest.php/wikibase/v0"

    @property
    def user_agent(self):
        return (
            "topic-curator (https://github.com/dpriskorn/WikidataTopicCurator/; "
            "User:So9q) python-requests/2.31.0"
        )

    @property
    def headers(self):
        return {"User-Agent": self.user_agent}
