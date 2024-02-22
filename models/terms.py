import logging
from copy import deepcopy

from pydantic import BaseModel

from models.enums import Source
from models.term import Term
from models.topic_item import TopicItem

logger = logging.getLogger(__name__)


class Terms(BaseModel):
    search_terms: set[Term] = set()

    def prepare(self):
        """Prepare all terms"""
        logger.debug(f"preparing {self.number_of_terms} terms")
        # Deepcopy to avoid errors
        search_terms = deepcopy(self.search_terms)
        search_terms = [term.prepared_term() for term in search_terms]
        # Remove duplicates and maintain order
        term_set = set(search_terms)
        # pprint(term_set)
        # logger.debug(f"length after duplicate removal: {len(term_set)}")
        self.search_terms = term_set
        logger.debug(
            f"number of terms after preparation and "
            f"duplicate removal: {self.number_of_terms}"
        )

    @property
    def number_of_terms(self) -> int:
        return len(self.search_terms)

    def get_terms_html(self, topic: TopicItem | None = None) -> str:
        """Build the table row html"""
        logger.debug("build_terms_html: running")
        html_lines = []
        all_terms = Terms()
        if topic is not None:
            logger.debug("got topic")
            label = Term(string=topic.get_label(), source=Source.LABEL)
            logger.info(f"label cache: {topic.get_label.cache_info()}")
            all_terms.search_terms.add(label)
            logger.debug(f"added label: {label.string}")
            for term in topic.get_aliases():
                alias = Term(string=term, source=Source.ALIAS)
                all_terms.search_terms.add(alias)
            logger.info(f"aliases cache: {topic.get_aliases.cache_info()}")
        else:
            logger.debug("got no topic")
        for user_term in self.search_terms:
            all_terms.search_terms.add(user_term)
        all_terms.prepare()
        count = all_terms.number_of_terms
        if count:
            logger.debug(f"preparing {count} terms")
            # mypy complains about this but I see no good
            # way of fixing it so we ignore it for now
            for term in all_terms.search_terms:  # type:ignore
                # if not type(term, Term):
                #     raise ValueError()
                # pprint(term.model_dump())
                html_lines.append(term.row_html)  # type:ignore
        else:
            logger.debug("all_terms were empty")
        return "\n".join(html_lines)
