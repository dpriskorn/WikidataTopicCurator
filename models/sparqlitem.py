from pydantic import BaseModel, Field


class SparqlItem(BaseModel):
    """This class models the data we get from SPARQL and converts it into a html row"""

    item: str  # this is required
    item_label: str = Field(default="No label found")
    instance_of_label: str = Field(default="No label found")
    publication_label: str = Field(default="No label found")
    doi: str = ""
    raw_full_resources: str = ""

    def __hash__(self):
        return hash(self.qid)

    def __eq__(self, other):
        return self.qid == other.qid

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
                <td><a href="{ self.qid_uri }" target="_blank">{ self.item_label }</a></td>
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
