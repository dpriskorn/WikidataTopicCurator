import logging

from models.query import Query

logger = logging.getLogger(__name__)


class PublishedArticleQuery(Query):
    @property
    def generate_279_minus_lines(self):
        lines = list()
        for levels in range(2, 15):
            subpath = "wdt:P921"
            path = subpath
            # We start at -1 because of the start path
            # e.g. number=2 => "wdt:P921/wdt:P921"
            for _ in range(1, levels):
                path += f"/{subpath}"
            lines.append(f"\t\tMINUS {{?item {path} wd:{self.parameters.topic.qid}. }}")
        return "\n".join(lines)

    def __build_query__(self):
        # This query uses https://www.w3.org/TR/sparql11-property-paths/ to
        # find subjects that are subclass of one another up to 3 hops away
        # This query also uses the https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI
        # which has a hardcoded limit of 10,000 items so you will never get more matches than that

        """
          MINUS {{?item wdt:P921/wdt:P279 wd:{self.parameters.topic.qid}. }}
          MINUS {{?item wdt:P921/wdt:P279/wdt:P279 wd:{self.parameters.topic.qid}. }}
          MINUS {{?item wdt:P921/wdt:P279/wdt:P279/wdt:P279 wd:{self.parameters.topic.qid}. }}
          MINUS {{?item wdt:P921/wdt:P279/wdt:P279/wdt:P279/wdt:P279 wd:{self.parameters.topic.qid}. }}
        """
        self.wdqs_query_string = f"""
            #{self.user_agent}
            SELECT DISTINCT ?item ?itemLabel ?instance_ofLabel 
            ?publicationLabel ?doi_id 
            (GROUP_CONCAT(DISTINCT ?full_resource; separator=",")
             as ?full_resources)
            WHERE {{
              hint:Query hint:optimizer "None".
              BIND(STR('{self.cirrussearch.cirrussearch_string}') as ?search_string)
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
              # Remove items that have a main subject that is subclass of this topic from the results
              # Do it for 15 levels because cell types has such a deep hierarchy
              {self.generate_279_minus_lines}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{self.lang}". }}
            }}
            GROUP BY ?item ?itemLabel ?instance_ofLabel ?publicationLabel ?doi_id
            LIMIT {self.calculated_limit}
        """
