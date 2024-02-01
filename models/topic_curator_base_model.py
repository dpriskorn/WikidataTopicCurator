import toolforge
from pydantic import BaseModel


class TopicCuratorBaseModel(BaseModel):
    @property
    def user_agent(self):
        return toolforge.set_user_agent(
            tool="Wikidata Topic Curator",
            url="https://www.wikidata.org/wiki/Wikidata:Tools/Wikidata_Topic_Curator",
            email="User:So9q",
        )
