import logging
from typing import List

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config as wbi_config

import config

wbi_config["USER_AGENT"] = config.user_agent
logger = logging.getLogger(__name__)


class TopicItem(BaseModel):
    qid: str

    @property
    def label(self):
        wbi = WikibaseIntegrator()
        return wbi.item.get(self.qid).labels.get(language="en").value or ""

    @property
    def aliases(self) -> List[str]:
        wbi = WikibaseIntegrator()
        aliases = wbi.item.get(self.qid).aliases.get(language="en")
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
