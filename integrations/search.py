import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)


async def search_tavily(query: str) -> list[dict]:
    """Search via Tavily."""
    try:
        from tavily import AsyncTavilyClient
        client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        resp = await client.search(query=query, search_depth="advanced", max_results=5)
        return resp.get("results", [])
    except Exception as e:
        logger.warning("Tavily search failed: %s", e)
        return []


async def search_douban(film_title: str, keywords: list[str]) -> list[dict]:
    """Search Douban reviews via Tavily."""
    kw = " ".join(keywords[:3])
    return await search_tavily(f"{film_title} {kw} 影评 豆瓣")

