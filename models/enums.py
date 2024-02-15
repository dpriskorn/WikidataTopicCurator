from enum import Enum


class Source(Enum):
    USER = "user"
    LABEL = "label"
    ALIAS = "alias"


class Subgraph(Enum):
    SCIENTIFIC_JOURNALS = "scientific_journals"  # dead:disable
    SCIENTIFIC_ARTICLES = "scientific_articles"
    RIKSDAGEN_DOCUMENTS = "riksdagen_documents"  # dead:disable
