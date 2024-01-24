from pydantic import BaseModel

from models.value import Value


class Item(BaseModel):
    """This class models the data we get from SPARQL and converts it into a html row"""

    item: Value
    itemLabel: Value
    # descriptionLabel: Value
    instance_ofLabel: Value = Value
    publicationLabel: Value = Value
    doi_id: Value = Value
    full_resource: Value = Value

    @property
    def qid_uri(self) -> str:
        return self.item.value

    @property
    def qid(self) -> str:
        return str(self.item.value.split("/")[-1])

    @property
    def label(self) -> str:
        return self.itemLabel.value

    # @property
    # def description(self):
    #     return self.descriptionLabel.value

    @property
    def instance_of_label(self) -> str:
        return self.instance_ofLabel.value or ""

    @property
    def doi(self):
        return self.doi_id.value or ""

    @property
    def doi_url(self):
        return f"https://dx.doi.org/{self.doi}"

    @property
    def link_to_full_resource(self) -> str:
        return self.full_resource.value or ""

    @property
    def publication_label(self) -> str:
        return self.publicationLabel.value or ""

    def row_html(self, count: int) -> str:
        # todo turn some of these into links
        baserow = f"""<tr>
                <td>{ count }</td>
                <td>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="checkbox-{self.qid}" name="selected_qids[]" value="{ self.qid }">
                        <label class="form-check-label" for="checkbox1"></label>
                    </div>
                </td>
                <td><a href="{ self.qid_uri }" target="_blank">{ self.label }</a></td>
                <td>{ self.instance_of_label }</td>
                <td>{ self.publication_label }</td>
                <td><a href="{ self.doi_url }" target="_blank">{ self.doi }</a></td>
        """
        if self.link_to_full_resource:
            row = (
                baserow
                + f"""
                            <td><a href="{ self.link_to_full_resource }" target="_blank">Link</a></td>
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
