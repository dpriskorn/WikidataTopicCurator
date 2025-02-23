from enum import Enum


class Source(Enum):
    """This is used to distinguish the source of terms"""

    USER = "user"
    LABEL = "label"
    ALIAS = "alias"


class Subgraph(Enum):
    """These are useful hardcoded subgraphs, we should avoid this and let users define subgraphs themselves"""

    # todo avoid hardcoding
    SCIENTIFIC_JOURNALS = "scientific_journals"  # dead:disable
    SCIENTIFIC_ARTICLES = "scientific_articles"
    RIKSDAGEN_DOCUMENTS = "riksdagen_documents"  # dead:disable
