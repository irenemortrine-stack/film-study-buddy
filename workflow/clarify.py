"""CLARIFYING: multi-round conversational follow-up."""
from integrations.deepseek import chat, chat_json
from integrations.feishu import send_text
from prompts.clarify_question import (
    CLARIFY_QUESTION, DETECT_DIMENSION, SWITCH_DIMENSION,
    SHOULD_STOP_CLARIFYING, FINALIZE_KEYWORDS,
)
from state.models import Clarification, Session


async def handle_clarify(open_id: str, message: str, session: Session) -> Session:
    # Store answer to last question
    if session.clarifications and session.clarifications[-1].answer == "":
        session.clarifications[-1].answer = message

    # Check user intent
    intent = await _detect_intent(message)

    if intent == "YES":
        return await _finalize(open_id, session)

    if intent == "SWITCH":
        if session.current_dimension:
            session.explored_dimensions.append(session.current_dimension)
        session.current_dimension = await _next_dimension(session)
        await send_text(open_id, f"好，我们聊聊「{session.current_dimension}」～", chat_id=session.chat_id or "")

    # Detect dimension from original review on first turn
    if not session.current_dimension:
        session.current_dimension = await _detect_dimension(session.original_review)

    question = await chat(
        "你是热爱电影的朋友。",
        CLARIFY_QUESTION.format(
            film_title=session.film_title or "这部电影",
            original_review=session.original_review,
            current_dimension=session.current_dimension,
            conversation_history=_format_history(session),
        ),
        temperature=0.8,
    )
    session.clarifications.append(Clarification(question=question, answer=""))
    session.clarification_round += 1
    await send_text(open_id, question, chat_id=session.chat_id or "")
    return session


async def _finalize(open_id: str, session: Session) -> Session:
    result = await chat_json(
        "你是电影理论研究者。",
        FINALIZE_KEYWORDS.format(
            film_title=session.film_title or "这部电影",
            original_review=session.original_review,
            conversation_history=_format_history(session),
        ),
    )
    session.keywords = result.get("keywords", session.keywords)
    session.state = "SEARCHING"
    await send_text(open_id, "好的，我去帮你找找相关的理论视角，稍等一下～", chat_id=session.chat_id or "")
    return session


async def _detect_intent(message: str) -> str:
    result = await chat(
        "你是一个意图分类器。",
        SHOULD_STOP_CLARIFYING.format(message=message),
        temperature=0.0,
    )
    return result.strip().upper()


async def _detect_dimension(original_review: str) -> str:
    result = await chat(
        "你是电影分析助手。",
        DETECT_DIMENSION.format(original_review=original_review),
        temperature=0.0,
    )
    return result.strip()


async def _next_dimension(session: Session) -> str:
    explored = ", ".join(session.explored_dimensions) if session.explored_dimensions else "无"
    result = await chat(
        "你是电影分析助手。",
        SWITCH_DIMENSION.format(explored_dimensions=explored),
        temperature=0.0,
    )
    return result.strip()


def _format_history(session: Session) -> str:
    lines = []
    for c in session.clarifications:
        lines.append(f"你：{c.question}")
        if c.answer:
            lines.append(f"我：{c.answer}")
    return "\n".join(lines)
