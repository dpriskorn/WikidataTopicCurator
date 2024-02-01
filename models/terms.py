import logging
from copy import deepcopy
from pprint import pprint
from typing import Set, Optional

from pydantic import BaseModel

from models.enums import Source
from models.term import Term
from models.topic import TopicItem

logger = logging.getLogger(__name__)


class Terms(BaseModel):
    search_terms: Set[Term] = set()

    def prepare(self):
        """Prepare all terms"""
        logger.debug(f"preparing {self.number_of_terms} terms")
        # Deepcopy to avoid errors
        search_terms = deepcopy(self.search_terms)
        search_terms = [term.prepared_term() for term in search_terms]
        # Remove duplicates and maintain order
        term_set = set(search_terms)
        pprint(term_set)
        # logger.debug(f"length after duplicate removal: {len(term_set)}")
        self.search_terms = term_set
        logger.debug(
            f"number of terms after preparation and "
            f"duplicate removal: {self.number_of_terms}"
        )

    @property
    def number_of_terms(self) -> int:
        return len(self.search_terms)

    def get_terms_html(self, topic: Optional[TopicItem] = None) -> str:
        """Build the table row html"""
        logger.debug("build_terms_html: running")
        html_lines = list()
        all_terms = Terms()
        if topic is not None:
            logger.debug("got topic")
            label = Term(string=topic.label, source=Source.LABEL)
            all_terms.search_terms.add(label)
            logger.debug(f"added label: {label.string}")
            for term in topic.aliases:
                alias = Term(string=term, source=Source.ALIAS)
                all_terms.search_terms.add(alias)
        else:
            logger.debug("got no topic")
        for user_term in self.search_terms:
            all_terms.search_terms.add(user_term)
        all_terms.prepare()
        count = all_terms.number_of_terms
        if count:
            logger.debug(f"preparing {count} terms")
            for term in all_terms.search_terms:
                # pprint(term.model_dump())
                html_lines.append(term.row_html)
        else:
            logger.debug(f"all_terms were empty")
        return "\n".join(html_lines)
