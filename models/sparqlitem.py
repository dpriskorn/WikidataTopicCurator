import re

from pydantic import BaseModel, Field

from deprecated.mediawiki import Revisions
from models.term import Term


class SparqlItem(BaseModel):
    """This class models the data we get from SPARQL and converts it into a html row"""

    item: str  # this is required
    item_label: str = Field(default="No label found")
    instance_of_label: str = Field(default="No label found")
    publication_label: str = Field(default="No label found")
    doi: str = ""
    raw_full_resources: str = ""
    term: Term
    cleaned_item_label: str = ""

    def __hash__(self):
        return hash(self.qid)

    def __eq__(self, other):
        return self.qid == other.qid

    def clean_item_label(self):
        print("cleaning")
        self.cleaned_item_label = self.item_label
        self.escape_single_quotes()
        self.remove_dashes()

    def escape_single_quotes(self):
        self.cleaned_item_label = self.cleaned_item_label.replace("'", "'")

    def remove_dashes(self):
        self.cleaned_item_label = self.cleaned_item_label.replace("-", " ").strip()

    @property
    def highlighted_item_label(self) -> str:
        if self.item_label != "No label found":
            self.clean_item_label()
            # inspired by https://stackoverflow.com/questions/68200973/highlight-multiple-substrings-in-a-string-in-python
            highlight_list = [self.term.string]
            highlight_str = r"\b(?:" + "|".join(highlight_list) + r")\b"
            replace_str = "<mark>\\g<0></mark>"
            text_highlight = re.sub(
                highlight_str, replace_str, self.cleaned_item_label, flags=re.IGNORECASE
            )
            print(text_highlight)
            return text_highlight
        else:
            return self.item_label

    @property
    def qid_uri(self) -> str:
        return self.item

    @property
    def qid(self) -> str:
        return str(self.item.split("/")[-1])

    @property
    def doi_url(self) -> str:
        return f"https://dx.doi.org/{self.doi}" if self.doi else ""

    def row_html(self, count: int) -> str:
        baserow = f"""<tr>
                <td>{ count }</td>
                <td>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="checkbox-{self.qid}" name="selected_qids[]" value="{ self.qid }">
                        <label class="form-check-label" for="checkbox1"></label>
                    </div>
                </td>
                <td><a href="{ self.qid_uri }" target="_blank">{ self.highlighted_item_label }</a></td>
                <td>{ self.instance_of_label }</td>
                <td>{ self.publication_label }</td>
                <td><a href="{ self.doi_url }" target="_blank">{ self.doi }</a></td>
        """
        if self.full_resources:
            row = (
                baserow
                + f"""
                            <td>{self.full_resources_html}</td>
            </tr>"""
            )
        else:
            row = (
                baserow
                + """
                            <td>-</td>
            </tr>"""
            )
        return row

    @property
    def full_resources(self) -> list[str]:
        return self.raw_full_resources.split(",")

    @property
    def full_resources_html(self):
        html = []
        for link in self.full_resources:
            html.append(f'<a href="{link}">Link</a>')
        return ", ".join(html)

    @property
    def has_been_undone(self) -> bool:
        revs = Revisions(item_qid="Q58505344", subject_qid="Q6279182")
        revs.fetch_revisions()
        return revs.has_been_undone
