from unittest import TestCase

from models.enums import Source
from models.sparqlitem import SparqlItem
from models.term import Term


class TestSparqlItem(TestCase):
    def test_clean_item_label(self):
        si = SparqlItem(
            term=Term(string="test", source=Source.LABEL),
            item="Q1",
            item_label="1. test-",
        )
        si.clean_item_label()
        print(si.cleaned_item_label)
        assert si.cleaned_item_label != ""
        assert si.cleaned_item_label == "1. test"

    def test_highlighted_item_label(self):
        si = SparqlItem(
            term=Term(string="test", source=Source.LABEL),
            item="Q1",
            item_label="1. test-",
        )
        assert si.highlighted_item_label == "1. <mark>test</mark>"
