import httpx
from config import settings


async def search_tavily(query: str) -> list[dict]:
    """Search academic sources via Tavily."""
    from tavily import AsyncTavilyClient
    client = AsyncTavilyClient(api_key=settings.tavily_api_key)
    resp = await client.search(
        query=query,
        search_depth="advanced",
        include_domains=["jstor.org", "academia.edu", "muse.jhu.edu"],
        max_results=5,
    )
    return resp.get("results", [])


async def search_serper(query: str) -> list[dict]:
    """Search via Serper (Google)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "num": 5},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("organic", [])


async def search_douban(film_title: str, keywords: list[str]) -> list[dict]:
    """Search Douban reviews via Serper with site restriction."""
    kw = " ".join(keywords[:3])
    query = f"site:douban.com {film_title} {kw} 影评"
    results = await search_serper(query)
    if not results:
        # Fallback without site restriction
        results = await search_serper(f"{film_title} {kw} 影评 豆瓣")
    return results
