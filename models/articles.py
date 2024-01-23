from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator

from models.published_article_query import PublishedArticleQuery


class Articles(BaseModel):
    qid: str
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
            main_subject_item=self.qid, search_string=self.label
        )
        self.query.start()
        print(self.query.number_of_results_text)

    def get_item_html_rows(self):
        if not self.query:
            raise ValueError("no self.query")
        html_list = [item.row_html() for item in self.query.items]
        html = "\n".join(html_list)
        return html
