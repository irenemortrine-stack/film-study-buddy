"""COLLECTING_REVIEW: extract keywords from initial review."""
# v2
from integrations.deepseek import chat, chat_json
from integrations.feishu import send_text
from prompts.extract_keywords import EXTRACT_KEYWORDS
from prompts.clarify_question import CLARIFY_QUESTION, DETECT_DIMENSION
from state.models import Clarification, Session


async def handle_collect(open_id: str, message: str, session: Session) -> Session:
    review = message.removeprefix("聊聊").strip()
    session.original_review = review

    result = await chat_json(
        "你是电影理论研究者。",
        EXTRACT_KEYWORDS.format(review=review),
    )
    session.film_title = result.get("film_title")
    session.keywords = result.get("keywords", [])

    # Detect dimension from initial review
    dimension = await chat(
        "你是电影分析助手。",
        DETECT_DIMENSION.format(original_review=review),
        temperature=0.0,
    )
    session.current_dimension = dimension.strip()

    # Ask first question in detected dimension
    question = await chat(
        "你是热爱电影的朋友。",
        CLARIFY_QUESTION.format(
            film_title=session.film_title or "这部电影",
            original_review=review,
            current_dimension=session.current_dimension,
            conversation_history="（无）",
        ),
        temperature=0.8,
    )
    session.clarifications.append(Clarification(question=question, answer=""))
    session.clarification_round = 1
    session.state = "CLARIFYING"

    await send_text(open_id, question, chat_id=session.chat_id or "")
    return session

