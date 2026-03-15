"""SELECTING_THEORY: handle card button callback."""
from integrations.deepseek import chat_json
from integrations.feishu import send_text
from prompts.essay_questions import ESSAY_QUESTIONS
from state.models import Session


async def handle_select(open_id: str, theory_index: int, session: Session) -> Session:
    session.selected_theory = session.theory_cards[theory_index]
    theory = session.selected_theory

    result = await chat_json(
        "你是电影研究导师。",
        ESSAY_QUESTIONS.format(
            film_title=session.film_title or "这部电影",
            theory_name=theory.name,
            core_idea=theory.core_idea,
            keywords=", ".join(session.keywords),
            original_review=session.original_review,
        ),
    )
    session.essay_questions = result.get("questions", [])
    session.essay_answers = []
    session.current_question_index = 0
    session.state = "ANSWERING_QUESTIONS"

    intro = f"好，我们用「{theory.name}」来分析这部电影。\n\n我会问你几个问题，你来回答，最后整理成一篇长评。\n\n第一个问题："
    await send_text(open_id, intro + session.essay_questions[0], chat_id=session.chat_id or "")
    return session
