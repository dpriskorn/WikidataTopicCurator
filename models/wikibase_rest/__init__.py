# import asyncio
# import logging
# from functools import lru_cache
# from typing import Any
#
# import aiohttp
#
# from models.exceptions import WikibaseRestApiError
# from models.topic_curator_base_model import TopicCuratorBaseModel
# from models.wikibase_rest.item import WikibaseRestItem
#
# logger = logging.getLogger(__name__)
#
#
# class WikibaseRestApi(TopicCuratorBaseModel):
#     qids: list[str]
#     lang: str
#
#     async def fetch_data(self, qid, endpoint):
#         async with aiohttp.ClientSession() as session:
#             url = f"{self.base_url}/entities/items/{qid}/{endpoint}"
#             async with session.get(url, headers=self.headers) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     return data
#                 else:
#                     raise WikibaseRestApiError(
#                         f"Failed to fetch data for ID {qid}, "
#                         f"endpoint {endpoint}. "
#                         f"Status code: {response.status}, see {url}"
#                     )
#
#     async def get_item_data(self, qid: str) -> Any:
#         tasks = [
#             self.fetch_data(qid, "labels"),
#             self.fetch_data(qid, "descriptions"),
#             self.fetch_data(qid, "aliases"),
#         ]
#         results = await asyncio.gather(*tasks)
#         label = results[0].get(self.lang, "Label missing in this language, please fix")
#         description = results[1].get(
#             self.lang, "Description missing in this language, please fix"
#         )
#         aliases = results[2].get(self.lang, [])
#         logger.debug(
#             f"Got {qid}. Label: '{label}'. Description: '{description}'. Aliases '{aliases}'"
#         )
#         from models.topic_item import TopicItem
#
#         return TopicItem(
#             qid=qid,
#             label=label,
#             description=description,
#             aliases=aliases,
#             lang=self.lang,
#         )
#
#     async def fetch_all_items(self) -> list[Any]:
#         logger.info("Fetching item data from Wikibase REST API asynchronously")
#         items = []
#         for qid in self.qids:
#             logger.debug(f"Fetching item data for {qid}")
#             item = await self.get_item_data(qid=qid)
#             items.append(item)
#         return items
