import logging
from copy import deepcopy
from pprint import pprint
from typing import Set

from pydantic import BaseModel

from models.term import Term

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
