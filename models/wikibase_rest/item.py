from pydantic import ConfigDict

from models.topic_curator_base_model import TopicCuratorBaseModel


class WikibaseRestItem(TopicCuratorBaseModel):
    """This is a generic Item in Wikibase"""

    qid: str
    lang: str
    label: str = ""
    description: str = ""
    aliases: list[str] = []
    label_missing: bool
    model_config = ConfigDict(extra="forbid")  # dead:disable

    # @property
    # def label(self):
    #     api = WikibaseRestApi(qid=self.qid, lang=self.lang, session=self.session)
    #     label = api.get_label
    #     if label is None or not label:
    #         label = "Label missing in this language, please fix"
    #     return label
    #
    # @property
    # def description(self) -> str:
    #     api = WikibaseRestApi(qid=self.qid, lang=self.lang, session=self.session)
    #     description = api        # Calculate execution time
    #         execution_time = time.time() - start_time
    #         print("Execution time:", execution_time, "seconds").get_description
    #     if description is None or not description:
    #         description = "Description missing in this language, please fix"
    #     return description
    #
    # @property
    # def aliases(self) -> list[str]:
    #     api = WikibaseRestApi(qid=self.qid, lang=self.lang, session=self.session)
    #     return api.get_aliases
