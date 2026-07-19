import asyncio
import duckduckgo_search

from ..schemas.search import SearchResult

class WebSearcher:
    def __init__(self) -> None:
        self._ddgs = duckduckgo_search.DDGS()


    async def search(self, query: str) -> list[SearchResult]:
        raw_data = await asyncio.to_thread(self._ddgs.text, query)
        return [
            SearchResult(
                url=item['href'],
                title=item['title'],
                description=item['body']
            )
            for item in raw_data
            ]
