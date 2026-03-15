"""ANSWERING_QUESTIONS: collect user answers one by one."""
from integrations.feishu import send_text
from state.models import Session


async def handle_answer(open_id: str, message: str, session: Session) -> Session:
    session.essay_answers.append(message)
    session.current_question_index += 1

    if session.current_question_index < len(session.essay_questions):
        next_q = session.essay_questions[session.current_question_index]
        idx = session.current_question_index + 1
        total = len(session.essay_questions)
        await send_text(open_id, f"（{idx}/{total}）{next_q}", chat_id=session.chat_id or "")
    else:
        session.state = "REVIEWING_ESSAY"
        await _show_essay_preview(open_id, session)

    return session


async def _show_essay_preview(open_id: str, session: Session) -> None:
    lines = [f"好的，这是你的分析草稿，确认后我帮你存到 Notion：\n"]
    for q, a in zip(session.essay_questions, session.essay_answers):
        lines.append(f"【{q}】\n{a}\n")
    lines.append("回复「确认」保存，或继续修改任意一条回答。")
    await send_text(open_id, "\n".join(lines), chat_id=session.chat_id or "")
