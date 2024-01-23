from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator
from urllib.parse import quote

import config
from models.published_article_query import PublishedArticleQuery

from wikibaseintegrator.wbi_config import config as wbi_config

wbi_config['USER_AGENT'] = config.user_agent


class Articles(BaseModel):
    qid: str
    limit: int
    cirrussearch_string: str
    cirrussearch_affix: str
    query: PublishedArticleQuery = None


    @property
    def is_valid_qid(self):
        if self.qid[1:].isdigit() and self.qid[:1] == "Q":
            return True
        else:
            return False

    @property
    def label(self):
        wbi = WikibaseIntegrator()
        return wbi.item.get(self.qid).labels.get(language="en").value or ""

    def get_items(self):
        """Lookup using sparql and convert to Items
        We want the P31 concatenated with ", "
        We want to sample P1433 so we only get one value
        We want english label and description
        We only want scientific items which have matching labels
        """
        self.query = PublishedArticleQuery(
            main_subject_item=self.qid,
            search_string=self.label,
            limit=self.limit,
            cirrussearch_string=self.cirrussearch_string,
            cirrussearch_affix=self.cirrussearch_affix
        )
        self.query.start()
        # print(self.query.number_of_results_text)

    def get_item_html_rows(self):
        if not self.query:
            raise ValueError("no self.query")
        count = 1
        html_list = list()
        for item in self.query.items:
            html_list.append(item.row_html(count=count))
            count += 1
        html = "\n".join(html_list)
        return html

    @property
    def cirrussearch_url(self) -> str:
        return f"https://www.wikidata.org/w/index.php?search={quote(self.query.cirrussearch_string)}&title=Special%3ASearch&profile=advanced&fulltext=1&ns0=1"
