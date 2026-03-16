"""SEARCHING: concurrent search + generate theory cards."""
import asyncio
from integrations.deepseek import chat_json
from integrations.feishu import send_text, send_theory_cards, upload_image
from integrations.search import search_tavily, search_douban
from integrations.card_renderer import html_to_png_bytes
from prompts.synthesize_theories import SYNTHESIZE_THEORIES
from prompts.image_prompt import build_visual_html
from state.models import Session, TheoryCard


async def handle_search(open_id: str, session: Session) -> Session:
    keywords_str = ", ".join(session.keywords)
    film = session.film_title or "电影"

    # Concurrent search
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
    # Ensure cards_data is a list
    if isinstance(cards_data, dict):
        cards_data = cards_data.get("cards", list(cards_data.values())[0] if cards_data else [])

    # Build TheoryCard objects + render images
    theory_cards: list[TheoryCard] = []
    image_keys: list[str] = []

    for card_data in cards_data[:3]:
        html = build_visual_html(
            card_data["name"],
            card_data.get("visual_description", ""),
            film,
        )
        png = await html_to_png_bytes(html)
        img_key = await upload_image(png)
        image_keys.append(img_key)

        theory_cards.append(TheoryCard(
            name=card_data["name"],
            key_figures=card_data.get("key_figures", ""),
            core_idea=card_data.get("core_idea", ""),
            mermaid=card_data.get("mermaid", ""),
            visual_html=html,
            source_links=card_data.get("source_links", []),
        ))

    session.theory_cards = theory_cards
    session.state = "SELECTING_THEORY"

    await send_theory_cards(
        open_id,
        [c.model_dump() for c in theory_cards],
        image_keys,
        chat_id=session.chat_id or "",
    )
    return session
