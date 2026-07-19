from app.services.web_search import WebSearcher


async def test_web_searcher():
    _test_query = 'For example'
    _web_searcher = WebSearcher()
    results = await _web_searcher.search(_test_query)
    assert results is not None
