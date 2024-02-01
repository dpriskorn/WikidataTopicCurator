import logging
from typing import List

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config

from models.topic_curator_base_model import TopicCuratorBaseModel

logger = logging.getLogger(__name__)


class TopicItem(TopicCuratorBaseModel):
    lang: str
    qid: str
    wbi: WikibaseIntegrator = WikibaseIntegrator()

    class Config:
        arbitrary_types_allowed = True

    def setup_wbi(self):
        wbi_config["USER_AGENT"] = self.user_agent

    @property
    def label(self):
        self.setup_wbi()
        return self.wbi.item.get(self.qid).labels.get(language=self.lang).value or ""

    @property
    def aliases(self) -> List[str]:
        self.setup_wbi()
        aliases = self.wbi.item.get(self.qid).aliases.get(language=self.lang)
        if aliases is not None:
            aliases = [str(alias) for alias in aliases]
            return aliases
        return list()

    @property
    def is_valid(self):
        # logger.debug(f'{self.qid.startswith("Q")} and {self.qid[1:].isdigit()}')
        return self.qid.startswith("Q") and self.qid[1:].isdigit()

    @property
    def url(self):
        return f"https://www.wikidata.org/wiki/{self.qid}"
