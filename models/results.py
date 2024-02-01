import logging
from typing import List

from pydantic import BaseModel
from wikibaseintegrator.wbi_config import config as wbi_config

import config
from models.item import Item
from models.parameters import Parameters
from models.published_article_query import PublishedArticleQuery
from models.query import Query

wbi_config["USER_AGENT"] = config.user_agent

logger = logging.getLogger(__name__)


class Results(BaseModel):
    queries: List[Query] = list()
    parameters: Parameters
    item_count: int = 0  # only used for honoring limit

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
                    parameters=self.parameters, term=term, item_count=self.item_count
                )
                self.queries.append(query)
                # Only run query if limit has not been reached
                if self.item_count < self.parameters.limit:
                    query.start()
                    self.item_count += len(query.items)
                    logger.info(
                        f"Added {len(query.items)} items, total items: {self.item_count}"
                    )
                else:
                    logger.debug("Limit reached")
        else:
            logger.debug("Falling back to self.parameters.topic.label as term")
            query = PublishedArticleQuery(
                parameters=self.parameters,
                term=self.parameters.topic.label,
            )
            query.start()
            self.queries.append(query)
            # self.items = self.query.items
        # print(self.query.number_of_results_text)

    @property
    def all_items(self) -> List[Item]:
        items = list()
        for query in self.queries:
            for item in query.items:
                items.append(item)
        return items

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
