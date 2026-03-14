from notion_client import AsyncClient
from config import settings
from state.models import Session

_client = AsyncClient(auth=settings.notion_token)


async def save_to_notion(session: Session) -> str:
    """Create a Notion page and return its URL."""
    theory = session.selected_theory
    title = f"{session.film_title or '未知电影'} — {theory.name if theory else '未知理论'}"

    # Build essay body from Q&A
    essay_blocks = []
    for i, (q, a) in enumerate(zip(session.essay_questions, session.essay_answers)):
        essay_blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": q}}]},
        })
        essay_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": a}}]},
        })

    # Mermaid chart block
    if theory and theory.mermaid:
        essay_blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "language": "mermaid",
                "rich_text": [{"type": "text", "text": {"content": theory.mermaid}}],
            },
        })

    page = await _client.pages.create(
        parent={"database_id": settings.notion_database_id},
        properties={
            "Title": {"title": [{"text": {"content": title}}]},
            "Film Title": {"rich_text": [{"text": {"content": session.film_title or ""}}]},
            "Original Review": {"rich_text": [{"text": {"content": session.original_review}}]},
            "Keywords": {"multi_select": [{"name": k} for k in session.keywords]},
            "Theory Name": {"select": {"name": theory.name if theory else ""}},
            "Key Figures": {"rich_text": [{"text": {"content": theory.key_figures if theory else ""}}]},
            "Theory Summary": {"rich_text": [{"text": {"content": theory.core_idea if theory else ""}}]},
            "Source Links": {"rich_text": [{"text": {"content": ", ".join(theory.source_links) if theory else ""}}]},
            "Created At": {"date": {"start": __import__("datetime").date.today().isoformat()}},
        },
        children=essay_blocks,
    )
    return page["url"]
