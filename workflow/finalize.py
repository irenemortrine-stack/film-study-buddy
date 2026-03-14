"""REVIEWING_ESSAY + FINALIZE: save to Notion."""
from integrations.feishu import send_text
from integrations.notion import save_to_notion
from state.models import Session


async def handle_finalize(open_id: str, message: str, session: Session) -> Session:
    if message.strip() in ("确认", "确认保存", "保存", "ok", "OK", "好的"):
        await send_text(open_id, "正在保存到 Notion，稍等～")
        url = await save_to_notion(session)
        await send_text(open_id, f"已保存！你的电影分析笔记：\n{url}\n\n下次想聊电影，发「聊聊」开始 :)")
        session.state = "IDLE"
    else:
        # Treat as an edit — find which question to update
        await send_text(open_id, "好的，你想修改哪条回答？请回复序号（如「1」）和新内容，格式：\n1 新的回答内容")
        session.state = "REVIEWING_ESSAY"
    return session


async def handle_edit_answer(open_id: str, message: str, session: Session) -> Session:
    """Handle inline edit: '2 新的回答内容'"""
    parts = message.split(" ", 1)
    if len(parts) == 2 and parts[0].isdigit():
        idx = int(parts[0]) - 1
        if 0 <= idx < len(session.essay_answers):
            session.essay_answers[idx] = parts[1].strip()
            await send_text(open_id, f"第 {idx+1} 条已更新。回复「确认」保存，或继续修改。")
            return session
    await send_text(open_id, "格式不对，请用「序号 新内容」，例如：\n2 这个场景让我想到了...")
    return session
