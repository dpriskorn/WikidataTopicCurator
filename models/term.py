import logging

from pydantic import BaseModel

from models.enums import Source

logger = logging.getLogger(__name__)


class Term(BaseModel):
    """This model handles everything related to a term
    Escaping, cleaning, lowercasing, etc.

    We choose not to include the source information here
    because it is only used in one view/page at the moment

    We don't consider the source when comparing terms"""

    string: str
    source: Source

    def __hash__(self):
        return hash(self.string)

    def __eq__(self, other):
        return self.string == other.string

    def prepared_term(self):
        logger.debug(f"preparing: {self.string}")
        self.lower()
        self.remove_dashes()
        # logger.debug(f"result: {self.string}")
        return self

    def remove_dashes(self):
        self.string = self.string.replace("-", " ")

    def lower(self):
        self.string = self.string.lower()

    @property
    def plus_formatted(self):
        return self.string.replace(" ", "+")

    @property
    def row_html(self) -> str:
        logger.debug(
            f"building html for term '{self.string}' with source '{self.source.value}'"
        )
        return f"""
        <tr>
            <td>                    
                <input type="checkbox" name="terms" value="{self.string}" checked=true>
            </td>
            <td>                    
                {self.string}
            </td>
            <td>                    
                <span class="source">{self.source.value}</span>
            </td>
        </tr>
        """
