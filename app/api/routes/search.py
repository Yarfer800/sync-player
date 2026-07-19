from fastapi import APIRouter, Query

from app.api.deps import CurrentUser
from app.schemas.search import SearchResult
from app.services.web_search import WebSearcher

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SearchResult])
async def search_web(
    query: str = Query(..., min_length=1),
    user: CurrentUser = None,  # Require authentication
):
    searcher = WebSearcher()
    results = await searcher.search(query)
    return results
