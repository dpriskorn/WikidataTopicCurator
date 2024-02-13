from pydantic import BaseModel


class TopicCuratorBaseModel(BaseModel):
    @property
    def user_agent(self):
        return ('topic-curator (https://github.com/dpriskorn/WikidataTopicCurator/; '
                'User:So9q) python-requests/2.31.0')
