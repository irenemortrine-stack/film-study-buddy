"""FastAPI entry point — Feishu webhook routes."""
import hashlib
import hmac
import json
import logging
import time

from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

from config import settings
from workflow.router import route_message, route_card_action

app = FastAPI(title="Film Study Buddy")


def _verify_feishu(timestamp: str, nonce: str, body: bytes, signature: str) -> bool:
    """Verify Feishu webhook signature."""
    key = settings.feishu_verification_token.encode()
    msg = (timestamp + nonce).encode() + body
    expected = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.post("/webhook/feishu/message")
async def feishu_message(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    data = json.loads(body)

    # URL verification challenge
    if data.get("type") == "url_verification":
        return JSONResponse({"challenge": data["challenge"]})

    # Signature verification (optional but recommended)
    # headers = request.headers
    # sig = headers.get("X-Lark-Signature", "")
    # ts = headers.get("X-Lark-Request-Timestamp", "")
    # nonce = headers.get("X-Lark-Request-Nonce", "")
    # if sig and not _verify_feishu(ts, nonce, body, sig):
    #     return JSONResponse({"code": 1, "msg": "invalid signature"}, status_code=403)

    logger.info("feishu raw payload keys: %s", list(data.keys()))

    event = data.get("event", {})
    msg = event.get("message", {})
    sender = event.get("sender", {})

    open_id = sender.get("sender_id", {}).get("open_id", "")
    message_id = msg.get("message_id", "")
    msg_type = msg.get("message_type", "")
    chat_id = msg.get("chat_id", "")

    logger.info("feishu message: open_id=%s msg_type=%s message_id=%s chat_id=%s", open_id, msg_type, message_id, chat_id)

    if msg_type != "text" or not open_id:
        logger.warning("dropped: msg_type=%s open_id=%s", msg_type, open_id)
        return JSONResponse({"code": 0})

    content = json.loads(msg.get("content", "{}"))
    raw_text = content.get("text", "")
    # Strip @mention tags that appear in group messages (e.g. "@_user_1 " or "<at ...>...</at>")
    import re
    text = re.sub(r"@\S+\s*", "", raw_text).strip()

    if text:
        background_tasks.add_task(route_message, open_id, text, message_id, chat_id)

    # Must respond within 3s
    return JSONResponse({"code": 0})


@app.post("/webhook/feishu/card")
async def feishu_card(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    data = json.loads(body)

    # URL verification challenge
    if data.get("type") == "url_verification":
        return JSONResponse({"challenge": data["challenge"]})

    open_id = data.get("open_id", "") or data.get("operator", {}).get("open_id", "")
    action = data.get("action", {})
    value = action.get("value", {})
    theory_index = value.get("theory_index")

    logger.info("card webhook: keys=%s open_id=%s theory_index=%s", list(data.keys()), open_id, theory_index)

    if open_id and theory_index is not None:
        background_tasks.add_task(route_card_action, open_id, int(theory_index))

    return JSONResponse({"code": 0})


@app.get("/health")
async def health():
    return {"status": "ok", "ts": int(time.time())}
