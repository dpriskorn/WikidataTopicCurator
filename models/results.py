import logging

from pydantic import BaseModel

from models.enums import Source
from models.query import Query
from models.sparqlitem import SparqlItem
from models.term import Term
from models.topicparameters import TopicParameters

logger = logging.getLogger(__name__)


class Results(BaseModel):
    lang: str
    parameters: TopicParameters
    queries: list[Query] = []

    # def __hash__(self):
    #     return hash(self.queries)

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
                query = Query(
                    parameters=self.parameters,
                    item_count=self.number_of_deduplicated_items,
                    lang=self.lang,
                    term=term,
                )
                # Only run query if limit has not been reached
                if self.number_of_deduplicated_items < self.parameters.limit:
                    # We get the items here to make the LRU cache work
                    items = query.run_and_get_items()
                    logger.info(f"qlever cache: {query.run_and_get_items.cache_info()}")
                    query.items = items
                else:
                    logger.debug("Limit reached")
                self.queries.append(query)
                logger.info(f"total items: {self.number_of_deduplicated_items}")
        else:
            logger.debug("Falling back to topic label as term")
            query = Query(
                parameters=self.parameters,
                term=Term(string=self.parameters.topic.get_label, source=Source.LABEL),
                lang=self.lang,
            )
            logger.info(f"label cache: {self.parameters.topic.get_label.cache_info()}")
            # We get the items here to make the LRU cache work
            items = query.run_and_get_items()
            logger.info(f"qlever cache: {query.run_and_get_items.cache_info()}")
            query.items = items
            self.queries.append(query)
            logger.info(f"total items: {self.number_of_deduplicated_items}")

    @property
    def all_items(self) -> set[SparqlItem]:
        """We deduplicate the items here and return a set"""
        items = []
        for query in self.queries:
            for item in query.items:
                items.append(item)
        return set(items)

    @property
    def excluded_items(self) -> set[SparqlItem]:
        """We deduplicate the items here and return a set"""
        logger.info("excluded_items: running")
        items = []
        item_count = 1
        query_count = 1
        for query in self.queries:
            logger.info(f"working on {query_count} out of {len(self.queries)}")
            for item in query.items:
                logger.info(f"working on {item_count} out of {len(query.items)}")
                if item.has_been_undone:
                    items.append(item)
                item_count += 1
            query_count += 1
        return set(items)

    @property
    def number_of_deduplicated_items(self):
        return len(self.all_items)

    @property
    def number_of_excluded_items(self):
        return len(self.excluded_items)

    def get_excluded_item_suggestion_html_rows(self):
        """This returns all suggestions that has been undone before"""
        logger.info("get_excluded_item_suggestion_html_rows: running")
        count = 1
        html_list = []
        for item in self.excluded_items:
            logger.info(f"working on {count} out of {self.number_of_excluded_items}")
            if item.has_been_undone:
                html_list.append(item.row_html(count=count))
                count += 1
        html = "\n".join(html_list)
        return html

    def get_item_suggestion_html_rows(self):
        """This returns all suggestions that has not been undone before"""
        logger.info("get_item_suggestion_html_rows: running")
        count = 1
        html_list = []
        for item in self.all_items:
            logger.info(
                f"working on {count} out of {self.number_of_deduplicated_items}"
            )
            if not item.has_been_undone:
                html_list.append(item.row_html(count=count))
                count += 1
        html = "\n".join(html_list)
        return html

    def get_query_html_rows(self):
        count = 1
        html_list = []
        for query in self.queries:
            html_list.append(query.row_html(count=count))
            logger.info(f"row html cache: {query.row_html.cache_info()}")
            count += 1
        html = "\n".join(html_list)
        return html
