import asyncio
import yt_dlp

from ..schemas.search import SearchResult

class WebSearcher:
    def __init__(self) -> None:
        pass

    async def search(self, query: str) -> list[SearchResult]:
        ydl_opts = {
            'quiet': True, 
            'extract_flat': 'in_playlist',
            'dump_single_json': True,
            'default_search': 'ytsearch10',
        }
        
        def _do_search():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(query, download=False)
                
        raw_data = await asyncio.to_thread(_do_search)
        
        results = []
        if raw_data and 'entries' in raw_data:
            for item in raw_data['entries']:
                results.append(SearchResult(
                    url=item.get('url', ''),
                    title=item.get('title', ''),
                    description=item.get('uploader', 'YouTube Video')
                ))
        return results
