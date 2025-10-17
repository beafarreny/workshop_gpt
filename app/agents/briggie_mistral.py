import os
import json
import httpx
from typing import AsyncGenerator, List
from dotenv import load_dotenv

from app.schemas.chat import Message

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
MISTRAL_BASE_URL = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")

if not MISTRAL_API_KEY:
    raise RuntimeError("⚠️ Missing MISTRAL_API_KEY in .env")


async def stream_mistral(messages: List[Message]) -> AsyncGenerator[str, None]:
    """
    Envía la conversación completa a la API de Mistral (versión online)
    y devuelve texto progresivamente mediante streaming.
    """
    url = f"{MISTRAL_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MISTRAL_MODEL,
        "messages": [m.model_dump() for m in messages],
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as r:
            async for line in r.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                    delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        yield delta
                except Exception:
                    continue
