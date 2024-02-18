from pydantic import ConfigDict

from models.topic_curator_base_model import TopicCuratorBaseModel


class WikibaseRestItem(TopicCuratorBaseModel):
    """This is a generic Item in Wikibase"""

    qid: str
    lang: str
    label: str = ""
    description: str = ""
    aliases: list[str] = []
    model_config = ConfigDict(extra="forbid")  # dead:disable
