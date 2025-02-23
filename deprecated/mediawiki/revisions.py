import logging

from pydantic import BaseModel, Field
from requests import Session

import config
from models.mediawiki.revision import Revision

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class Revisions(BaseModel):
    """Manages a collection of revisions and provides filtering.
    Fetches revisions based on a qid"""

    item_qid: str
    subject_qid: str
    revisions: list[Revision] = Field(
        default_factory=list, description="List of revisions"
    )
    session: Session = Session()
    model_config = {"arbitrary_types_allowed": True}  # dead: disable

    # @property
    # def filter_by_subject_qid(self) -> List[Revision]:
    #     """Filter revisions where the comment contains the given keyword."""
    #     return [rev for rev in self.revisions if "[[Property:P921]]" and f"[[{self.item_qid}]]" in rev.comment]

    @property
    def filter_by_subject_qid(self) -> list[Revision]:
        """
        Filter revisions where the comment contains both Property:P921 and the item QID.

        Returns:
            List[Revision]: List of revisions matching the filter criteria
        """
        filtered_revisions = []

        logger.debug(f"Starting to filter revisions for item QID: {self.item_qid}")
        logger.debug(f"Total revisions to process: {len(self.revisions)}")

        for rev in self.revisions:
            required_terms = ["[[Property:P921]]", f"[[{self.subject_qid}]]"]
            if all(term in rev.comment for term in required_terms):
                filtered_revisions.append(rev)
                logger.debug(f"Found matching revision: {rev.comment}")
            else:
                # Log which required terms are missing
                missing_terms = [
                    term for term in required_terms if term not in rev.comment
                ]
                logger.debug(f"Non-matching revision: {rev.comment}")
                logger.debug(f"Missing terms: {missing_terms}")

        logger.debug(
            f"Finished filtering. Found {len(filtered_revisions)} matching revisions"
        )
        return filtered_revisions

    @property
    def has_been_undone(self) -> bool:
        revs = self.filter_by_subject_qid
        if revs:
            # check all revisions for undone operations
            for undo_rev in revs:
                for rev in self.revisions:
                    if f"undo:0||{undo_rev.id}|" in rev.comment:
                        return True
        # return false if no revs or no revs with undone
        return False

    @property
    def has_been_removed(self):  # dead: disable
        # todo check if a user removed it without using the undo function
        pass

    @property
    def has_been_undone_or_removed(self):  # dead: disable
        # todo meta method
        pass

    def fetch_revisions(self) -> None:
        """Fetch revisions from the Wikidata API and return a Revisions instance."""
        # inspired by https://stackoverflow.com/questions/60597841/how-to-access-wikidata-revision-history
        # todo get whole history, not just the first 10000
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": self.item_qid,
            "formatversion": "2",
            "rvprop": "ids|comment",
            "rvslots": "main",
            "rvlimit": "10000",
            "rvdir": "newer",
        }

        response = self.session.get(url=url, params=params)
        data = response.json()
        # print(data)
        # exit()

        for page in data.get("query", {}).get("pages", []):
            for rev in page.get("revisions", []):
                revision = Revision(id=rev["revid"], comment=rev.get("comment", ""))
                self.revisions.append(revision)
