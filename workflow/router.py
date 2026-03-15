"""State machine router — dispatches messages to the right workflow handler."""
import logging
from state.store import get_session, save_session, SessionLock
from state.models import Session
from integrations.feishu import send_text

logger = logging.getLogger(__name__)


async def route_message(open_id: str, message: str, message_id: str) -> None:
    try:
        async with SessionLock(open_id):
            session = await get_session(open_id)

            # Idempotency check
            if message_id in session.processed_message_ids:
                return
            session.processed_message_ids = (session.processed_message_ids + [message_id])[-50:]

            session = await _dispatch(open_id, message, session)
            await save_session(open_id, session)
    except Exception:
        logger.exception("route_message failed for open_id=%s message_id=%s", open_id, message_id)


async def route_card_action(open_id: str, theory_index: int) -> None:
    try:
        async with SessionLock(open_id):
            session = await get_session(open_id)
            if session.state != "SELECTING_THEORY":
                return
            from workflow.select import handle_select
            session = await handle_select(open_id, theory_index, session)
            await save_session(open_id, session)
    except Exception:
        logger.exception("route_card_action failed for open_id=%s theory_index=%s", open_id, theory_index)


async def _dispatch(open_id: str, message: str, session: Session) -> Session:
    state = session.state

    if state == "IDLE":
        if message.startswith("聊聊"):
            from workflow.collect import handle_collect
            return await handle_collect(open_id, message, session)
        else:
            await send_text(open_id, "发「聊聊 + 你的观影感受」开始分析，例如：\n聊聊 女主角好压抑，家庭关系扭曲")
            return session

    if state == "CLARIFYING":
        from workflow.clarify import handle_clarify
        session = await handle_clarify(open_id, message, session)
        # If clarify moved us to SEARCHING, trigger search immediately
        if session.state == "SEARCHING":
            session = await _trigger_search(open_id, session)
        return session

    if state == "SELECTING_THEORY":
        await send_text(open_id, "请点击上方卡片中的按钮选择一个理论视角～")
        return session

    if state == "ANSWERING_QUESTIONS":
        from workflow.answer import handle_answer
        return await handle_answer(open_id, message, session)

    if state == "REVIEWING_ESSAY":
        # Check if it's an edit command (starts with digit)
        stripped = message.strip()
        if stripped and stripped[0].isdigit() and " " in stripped:
            from workflow.finalize import handle_edit_answer
            return await handle_edit_answer(open_id, message, session)
        from workflow.finalize import handle_finalize
        return await handle_finalize(open_id, message, session)

    await send_text(open_id, "发「聊聊 + 你的观影感受」开始新的分析。")
    return session


async def _trigger_search(open_id: str, session: Session) -> Session:
    from workflow.search import handle_search
    return await handle_search(open_id, session)
