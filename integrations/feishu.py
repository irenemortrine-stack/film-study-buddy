"""Feishu (Lark) messaging and interactive card integration."""
import httpx
from config import settings

_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
_MSG_URL = "https://open.feishu.cn/open-apis/im/v1/messages"
_UPLOAD_URL = "https://open.feishu.cn/open-apis/im/v1/files"

_cached_token: dict = {"token": None, "expire": 0}


async def _get_token() -> str:
    import time
    now = time.time()
    if _cached_token["token"] and now < _cached_token["expire"] - 60:
        return _cached_token["token"]
    async with httpx.AsyncClient() as client:
        resp = await client.post(_TOKEN_URL, json={
            "app_id": settings.feishu_app_id,
            "app_secret": settings.feishu_app_secret,
        })
        data = resp.json()
    _cached_token["token"] = data["tenant_access_token"]
    _cached_token["expire"] = now + data["expire"]
    return _cached_token["token"]


async def send_text(open_id: str, text: str, chat_id: str = "") -> None:
    import json
    token = await _get_token()
    if chat_id:
        receive_id_type, receive_id = "chat_id", chat_id
    else:
        receive_id_type, receive_id = "open_id", open_id
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{_MSG_URL}?receive_id_type={receive_id_type}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "receive_id": receive_id,
                "msg_type": "text",
                "content": json.dumps({"text": text}),
            },
        )


async def upload_image(png_bytes: bytes) -> str:
    """Upload image bytes to Feishu and return image_key."""
    import io
    token = await _get_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://open.feishu.cn/open-apis/im/v1/images",
            headers={"Authorization": f"Bearer {token}"},
            data={"image_type": "message"},
            files={"image": ("card.png", io.BytesIO(png_bytes), "image/png")},
        )
        data = resp.json()
    return data["data"]["image_key"]


async def send_theory_cards(open_id: str, cards: list[dict], image_keys: list[str], chat_id: str = "") -> None:
    """Send interactive card with 3 theory options."""
    import json
    token = await _get_token()

    elements = []
    for i, card in enumerate(cards):
        img_key = image_keys[i] if i < len(image_keys) else None
        if img_key:
            elements.append({
                "tag": "img",
                "img_key": img_key,
                "alt": {"tag": "plain_text", "content": card["name"]},
            })
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{card['name']}**\n{card['key_figures']}\n\n{card['core_idea']}",
            },
        })
        # Logic chain as plain text
        mermaid_text = card.get("mermaid", "").replace("flowchart LR\n", "").replace("-->", "→")
        elements.append({
            "tag": "div",
            "text": {"tag": "plain_text", "content": mermaid_text},
        })
        elements.append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": f"选择「{card['name']}」"},
                "type": "primary",
                "value": {"theory_index": i},
            }],
        })
        if i < len(cards) - 1:
            elements.append({"tag": "hr"})

    card_content = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "为你找到 3 个理论视角，选一个深入分析吧"},
            "template": "blue",
        },
        "elements": elements,
    }

    async with httpx.AsyncClient() as client:
        if chat_id:
            receive_id_type, receive_id = "chat_id", chat_id
        else:
            receive_id_type, receive_id = "open_id", open_id
        await client.post(
            f"{_MSG_URL}?receive_id_type={receive_id_type}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "receive_id": receive_id,
                "msg_type": "interactive",
                "content": json.dumps(card_content),
            },
        )
