"""COLLECTING_REVIEW: extract keywords from initial review."""
import json
from integrations.deepseek import chat_json
from integrations.feishu import send_text
from prompts.extract_keywords import EXTRACT_KEYWORDS
from prompts.clarify_question import CLARIFY_QUESTION
from state.models import Session


async def handle_collect(open_id: str, message: str, session: Session) -> Session:
    # Strip trigger word
    review = message.removeprefix("聊聊").strip()
    session.original_review = review

    # Extract film title + keywords
    result = await chat_json(
        "你是电影理论研究者。",
        EXTRACT_KEYWORDS.format(review=review),
    )
    session.film_title = result.get("film_title")
    session.keywords = result.get("keywords", [])

    # Ask first clarifying question
    film_label = session.film_title or "这部电影"
    question = await _ask_clarify(session)
    session.clarification_round = 1
    session.state = "CLARIFYING"

    await send_text(open_id, question)
    return session


async def _ask_clarify(session: Session) -> str:
    from integrations.deepseek import chat
    history = "\n".join(
        f"我：{c.answer}\n你：{c.question}" for c in session.clarifications
    )
    return await chat(
        "你是热爱电影的朋友。",
        CLARIFY_QUESTION.format(
            film_title=session.film_title or "这部电影",
            original_review=session.original_review,
            keywords=", ".join(session.keywords),
            conversation_history=history or "（无）",
        ),
        temperature=0.8,
    )
