import asyncio
import logging

import aiohttp

from models.exceptions import WikibaseRestApiError
from models.topic_curator_base_model import TopicCuratorBaseModel
from models.wikibase_rest.item import WikibaseRestItem

logger = logging.getLogger(__name__)


class WikibaseRestApi(TopicCuratorBaseModel):
    qids: list[str]
    lang: str

    async def fetch_data(self, qid, endpoint):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/entities/items/{qid}/{endpoint}"
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    raise WikibaseRestApiError(
                        f"Failed to fetch data for ID {qid}, "
                        f"endpoint {endpoint}. "
                        f"Status code: {response.status}, see {url}"
                    )

    async def get_item_data(self, qid):
        tasks = [
            self.fetch_data(qid, "labels"),
            self.fetch_data(qid, "descriptions"),
            self.fetch_data(qid, "aliases"),
        ]
        results = await asyncio.gather(*tasks)
        return WikibaseRestItem(
            qid=qid,
            label=results[0].get(self.lang, ""),
            description=results[1].get(self.lang, ""),
            aliases=results[2].get(self.lang, []),
            lang=self.lang,
        )

    async def fetch_all_items(self) -> list[WikibaseRestItem]:
        logger.info("Fetching item data from Wikibase REST API asynchronously")
        items = []
        for qid in self.qids:
            item = await self.get_item_data(qid=qid)
            items.append(item)
        return items
