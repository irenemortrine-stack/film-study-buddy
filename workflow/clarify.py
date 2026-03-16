"""CLARIFYING: multi-round conversational follow-up."""
from integrations.deepseek import chat, chat_json
from integrations.feishu import send_text
from prompts.clarify_question import CLARIFY_QUESTION, SHOULD_STOP_CLARIFYING, FINALIZE_KEYWORDS
from state.models import Clarification, Session

async def handle_clarify(open_id: str, message: str, session: Session) -> Session:
    # Record user's answer to the last question
    last_question = session.clarifications[-1].question if session.clarifications else ""
    # The previous question was sent but not yet stored with answer — store it now
    # (question was sent in previous turn; we pair it with this answer)
    if session.clarifications and session.clarifications[-1].answer == "":
        session.clarifications[-1].answer = message
    else:
        # Find the pending question (stored without answer)
        session.clarifications.append(Clarification(question=last_question, answer=message))

    should_stop = await _wants_to_stop(message)

    if should_stop:
        # Finalize keywords
        history = _format_history(session)
        result = await chat_json(
            "你是电影理论研究者。",
            FINALIZE_KEYWORDS.format(
                film_title=session.film_title or "这部电影",
                original_review=session.original_review,
                conversation_history=history,
            ),
        )
        session.keywords = result.get("keywords", session.keywords)
        session.state = "SEARCHING"
        await send_text(open_id, "好的，我去帮你找找相关的理论视角，稍等一下～", chat_id=session.chat_id or "")
    else:
        # Ask next question
        history = _format_history(session)
        question = await chat(
            "你是热爱电影的朋友。",
            CLARIFY_QUESTION.format(
                film_title=session.film_title or "这部电影",
                original_review=session.original_review,
                keywords=", ".join(session.keywords),
                conversation_history=history,
            ),
            temperature=0.8,
        )
        session.clarifications.append(Clarification(question=question, answer=""))
        session.clarification_round += 1
        await send_text(open_id, question, chat_id=session.chat_id or "")

    return session


async def _wants_to_stop(message: str) -> bool:
    from integrations.deepseek import chat
    result = await chat(
        "你是一个意图分类器。",
        SHOULD_STOP_CLARIFYING.format(message=message),
        temperature=0.0,
    )
    return result.strip().upper() == "YES"


def _format_history(session: Session) -> str:
    lines = []
    for c in session.clarifications:
        lines.append(f"你：{c.question}")
        if c.answer:
            lines.append(f"我：{c.answer}")
    return "\n".join(lines)
