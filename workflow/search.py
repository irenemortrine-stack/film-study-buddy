"""SEARCHING: concurrent search + generate theory cards."""
import asyncio
from integrations.deepseek import chat_json
from integrations.feishu import send_text, send_theory_cards
from integrations.search import search_tavily, search_douban
from prompts.synthesize_theories import SYNTHESIZE_THEORIES
from state.models import Session, TheoryCard


async def handle_search(open_id: str, session: Session) -> Session:
    keywords_str = ", ".join(session.keywords)
    film = session.film_title or "电影"

    academic_query = f"film theory {keywords_str} academic"
    academic_results, review_results = await asyncio.gather(
        search_tavily(academic_query),
        search_douban(film, session.keywords),
    )

    def _fmt(results: list[dict]) -> str:
        lines = []
        for r in results[:5]:
            title = r.get("title", "")
            url = r.get("url", r.get("link", ""))
            snippet = r.get("content", r.get("snippet", ""))
            lines.append(f"- {title}: {snippet} ({url})")
        return "\n".join(lines) or "（无结果）"

    cards_data = await chat_json(
        "你是电影理论专家。",
        SYNTHESIZE_THEORIES.format(
            film_title=film,
            keywords=keywords_str,
            academic_results=_fmt(academic_results),
            review_results=_fmt(review_results),
        ),
    )
    if isinstance(cards_data, dict):
        cards_data = cards_data.get("cards", list(cards_data.values())[0] if cards_data else [])

    theory_cards: list[TheoryCard] = []
    for card_data in cards_data[:3]:
        theory_cards.append(TheoryCard(
            name=card_data["name"],
            key_figures=card_data.get("key_figures", ""),
            core_idea=card_data.get("core_idea", ""),
            mermaid=card_data.get("mermaid", ""),
            visual_html="",
            source_links=card_data.get("source_links", []),
        ))

    session.theory_cards = theory_cards
    session.state = "SELECTING_THEORY"

    await send_theory_cards(
        open_id,
        [c.model_dump() for c in theory_cards],
        [],
        chat_id=session.chat_id or "",
    )
    return session

