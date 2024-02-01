import logging
from pprint import pprint
from typing import Optional

from pydantic import BaseModel

from models.Term import Term
from models.enums import Source
from models.terms import Terms
from models.topic import TopicItem

logger = logging.getLogger(__name__)


class HtmlTermsBuilder(BaseModel):
    user_terms: Terms
    topic: Optional[TopicItem] = None

    @staticmethod
    def build_term_row(term: Term) -> str:
        if term is None:
            raise ValueError("term was None")
        logger.debug(
            f"building html for term '{term.string}' with source '{str(term.source)}'"
        )
        return f"""
        <tr>
            <td>                    
                <input type="checkbox" name="terms" value="{term.string}" checked=true>
            </td>
            <td>                    
                {term.string}
            </td>
            <td>                    
                <span class="source">{str(term.source)}</span>
            </td>
        </tr>
        """

    @property
    def get_terms_html(self) -> str:
        """Build the table row html"""
        logger.debug("build_terms_html: running")
        html_lines = list()
        all_terms = Terms()
        if self.topic is not None:
            logger.debug("got topic")
            label = Term(string=self.topic.label, source=Source.LABEL)
            all_terms.search_terms.add(label)
            logger.debug(f"added label: {label.string}")
            for term in self.topic.aliases:
                alias = Term(string=term, source=Source.ALIAS)
                all_terms.search_terms.add(alias)
        for user_term in self.user_terms.search_terms:
            all_terms.search_terms.add(user_term)
        all_terms.prepare()
        count = all_terms.number_of_terms
        if count:
            logger.debug(f"preparing {count} terms")
            for term in all_terms.search_terms:
                pprint(term.model_dump())
                html_lines.append(self.build_term_row(term=term))
        else:
            logger.debug(f"all_terms were empty")
        return "\n".join(html_lines)
