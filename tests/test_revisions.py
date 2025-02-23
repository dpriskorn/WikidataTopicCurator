from models.mediawiki.revisions import Revisions


class TestRevisions:
    def test_fetch_revisions(self):
        revs = Revisions(item_qid="Q58505344", subject_qid="")
        revs.fetch_revisions()
        # print(revs.revisions)
        assert len(revs.revisions) > 0

    def test_filter_by_subject_qid(self):
        revs = Revisions(item_qid="Q58505344", subject_qid="Q6279182")
        revs.fetch_revisions()
        # print(revs.revisions)
        assert len(revs.revisions) > 0
        filtered = revs.filter_by_subject_qid
        print(filtered)
        assert len(filtered) > 0

    def test_has_been_undone(self):
        revs = Revisions(item_qid="Q58505344", subject_qid="Q6279182")
        revs.fetch_revisions()
        # print(revs.revisions)
        assert len(revs.revisions) > 0
        filtered = revs.filter_by_subject_qid
        print(filtered)
        assert revs.has_been_undone is True
