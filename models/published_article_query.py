import logging

import config
from models.query import Query

logger = logging.getLogger(__name__)


class PublishedArticleQuery(Query):
    @property
    def calculated_limit(self) -> int:
        return self.parameters.limit - self.item_count

    def __build_query__(self):
        # This query uses https://www.w3.org/TR/sparql11-property-paths/ to
        # find subjects that are subclass of one another up to 3 hops away
        # This query also uses the https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI
        # which has a hardcoded limit of 10,000 items so you will never get more matches than that
        # This query use regex to match beginning, middle and end of the label of matched items
        # The replacing lines should match the similar python replacements in cleaning.py
        # The replacing with "\\\\\\\\" becomes "\\\\" after leaving python and then it works in
        # SPARQL where it becomes "\\" and thus match a single backslash
        """disabled:
                # Label
        ?item rdfs:label ?label.
        BIND(REPLACE(LCASE(?label), ",", "") as ?label1)
        BIND(REPLACE(?label1, ":", "") as ?label2)
        BIND(REPLACE(?label2, ";", "") as ?label3)
        BIND(REPLACE(?label3, "\\\\(", "") as ?label4)
        BIND(REPLACE(?label4, "\\\\)", "") as ?label5)
        BIND(REPLACE(?label5, "\\\\[", "") as ?label6)
        BIND(REPLACE(?label6, "\\\\]", "") as ?label7)
        BIND(REPLACE(?label7, "\\\\\\\\", "") as ?label8)
        BIND(?label8 as ?cleaned_label)
        FILTER(CONTAINS(?cleaned_label, ' {self.search_string.lower()} '@{self.lang}) ||
               REGEX(?cleaned_label, '.* {self.search_string.lower()}$'@{self.lang}) ||
               REGEX(?cleaned_label, '^{self.search_string.lower()} .*'@{self.lang}))
        """
        self.wdqs_query_string = f"""
            #{config.user_agent}
            SELECT DISTINCT ?item ?itemLabel ?instance_ofLabel ?publicationLabel ?doi_id ?full_resource
            WHERE {{
              hint:Query hint:optimizer "None".
              BIND(STR('{self.cirrussearch_string}') as ?search_string)
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                mwapi:srsearch ?search_string.
                ?title wikibase:apiOutput mwapi:title.
              }}
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item wdt:P31 ?instance_of.
              optional{{
              ?item wdt:P1433 ?publication.
                }}
              optional{{
              ?item wdt:P356 ?doi_id.
                }}
              optional{{
              ?item wdt:P953 ?full_resource.
              }}
              # Remove those that are subclass of this topic from the results
              MINUS {{?item wdt:P921/wdt:P279 wd:{self.parameters.topic.qid}. }}
              MINUS {{?item wdt:P921/wdt:P279/wdt:P279 wd:{self.parameters.topic.qid}. }}
              MINUS {{?item wdt:P921/wdt:P279/wdt:P279/wdt:P279 wd:{self.parameters.topic.qid}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            limit {self.calculated_limit}
            """
