import logging
from typing import List, Set

from pydantic import BaseModel

from models.enums import Source
from models.item import Item
from models.parameters import Parameters
from models.published_article_query import PublishedArticleQuery
from models.query import Query
from models.term import Term

logger = logging.getLogger(__name__)


class Results(BaseModel):
    lang: str
    parameters: Parameters
    queries: List[Query] = list()

    def get_items(self):
        """Lookup using sparql and convert to Items
        We want the P31 concatenated with ", "
        We want to sample P1433 so we only get one value
        We want english label and description
        We only want scientific items which have matching labels
        """
        if self.parameters.terms.search_terms:
            """We runt multiple queries because CirrusSearch
            does not support the logical OR operator"""
            for term in self.parameters.terms.search_terms:
                query = PublishedArticleQuery(
                    parameters=self.parameters,
                    item_count=self.number_of_deduplicated_items,
                    lang=self.lang,
                    term=term,
                )
                self.queries.append(query)
                # Only run query if limit has not been reached
                if self.number_of_deduplicated_items < self.parameters.limit:
                    query.start()
                    logger.info(
                        f"total items: {self.number_of_deduplicated_items}"
                    )
                else:
                    logger.debug("Limit reached")
        else:
            logger.debug("Falling back to self.parameters.topic.label as term")
            query = PublishedArticleQuery(
                parameters=self.parameters,
                term=Term(string=self.parameters.topic.label, source=Source.LABEL),
                lang=self.lang,
            )
            query.start()
            self.queries.append(query)

    @property
    def all_items(self) -> Set[Item]:
        """We deduplicate the items here and return a set"""
        items = list()
        for query in self.queries:
            for item in query.items:
                items.append(item)
        return set(items)

    @property
    def number_of_deduplicated_items(self):
        return len(self.all_items)

    def get_item_html_rows(self):
        count = 1
        html_list = list()
        for item in self.all_items:
            html_list.append(item.row_html(count=count))
            count += 1
        html = "\n".join(html_list)
        return html

    def get_query_html_rows(self):
        count = 1
        html_list = list()
        for query in self.queries:
            html_list.append(query.row_html(count=count))
            count += 1
        html = "\n".join(html_list)
        return html
