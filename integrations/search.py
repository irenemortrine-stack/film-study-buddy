import asyncio
import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

_SEARCH_TIMEOUT = 10  # seconds


async def search_tavily(query: str) -> list[dict]:
    """Search via Tavily. Returns empty list on timeout or error."""
    try:
        from tavily import AsyncTavilyClient
        client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        resp = await asyncio.wait_for(
            client.search(query=query, search_depth="advanced", max_results=5),
            timeout=_SEARCH_TIMEOUT,
        )
        return resp.get("results", [])
    except asyncio.TimeoutError:
        logger.warning("Tavily search timed out after %ss for query: %s", _SEARCH_TIMEOUT, query)
        return []
    except Exception as e:
        logger.warning("Tavily search failed: %s", e)
        return []


async def search_douban(film_title: str, keywords: list[str]) -> list[dict]:
    """Search Douban reviews via Tavily."""
    kw = " ".join(keywords[:3])
    return await search_tavily(f"{film_title} {kw} 影评 豆瓣")

