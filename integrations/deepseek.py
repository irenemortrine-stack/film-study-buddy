import json
from openai import AsyncOpenAI
from config import settings

_client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
)


async def chat(system: str, user: str, temperature: float = 0.7) -> str:
    resp = await _client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


async def chat_json(system: str, user: str) -> dict | list:
    """Call DeepSeek and parse JSON response."""
    text = await chat(system, user, temperature=0.3)
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)
