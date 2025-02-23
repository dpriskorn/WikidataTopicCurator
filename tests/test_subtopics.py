from unittest import TestCase

from models.subtopics import Subtopics


class TestSubtopics(TestCase):
    def test_subtopics_json(self):
        subtopics = Subtopics(
            qid="Q2827132",
            lang="en",
        )
        subtopics.fetch_subtopics()
        assert subtopics.data != {}
        subtopics.parse_into_topic_items()
        assert len(subtopics.subtopics) > 0
        assert subtopics.subtopics_json != []

    def test_fetch_subtopics(self):
        subtopics = Subtopics(
            qid="Q2827132",
            lang="en",
        )
        subtopics.fetch_subtopics()
        assert subtopics.data != {}

    def test_parse_into_topic_items(self):
        subtopics = Subtopics(
            qid="Q2827132",
            lang="en",
        )
        subtopics.fetch_subtopics()
        assert subtopics.data != {}
        subtopics.parse_into_topic_items()
        assert len(subtopics.subtopics) > 0
