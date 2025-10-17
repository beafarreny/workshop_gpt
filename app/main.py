from __future__ import annotations
import os
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from app.schemas.chat import Message, ChatIn
from app.utils.storage import load_history, save_history
from app.agents.briggie_gpt import agent  # 👈 nuevo import

# ==== CONFIGURACIÓN ====
load_dotenv()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")

app = FastAPI(title="Briggie GPT (pydantic_ai version)")

# ==== CORS ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:5500", "http://127.0.0.1:5500", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== HISTORIAL ====
HISTORY: Dict[str, List[Message]] = {}
raw_data = load_history()
for user_id, msgs in raw_data.items():
    HISTORY[user_id] = [Message(**m) for m in msgs]

def _ensure_user(user_id: str) -> List[Message]:
    if user_id not in HISTORY:
        HISTORY[user_id] = []
    return HISTORY[user_id]


# ==== ENDPOINTS ====

@app.get("/health")
async def health():
    return {"status": "ok", "provider": f"openai:{os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}", "mode": "online"}


@app.get("/chat-system/chat/{user_id}")
async def get_chat(user_id: str):
    return _ensure_user(user_id)


@app.post("/chat-system/chat/{user_id}")
async def post_chat(user_id: str, body: ChatIn):
    msgs = _ensure_user(user_id)
    msg = Message(role="user", content=body.content)
    msgs.append(msg)
    save_history({k: [m.model_dump() for m in v] for k, v in HISTORY.items()})
    return {"role": "user", "content": body.content}


@app.post("/chat-system/chat-streaming/{user_id}")
async def chat_stream(user_id: str, body: ChatIn):
    msgs = _ensure_user(user_id)

    async def token_generator():
        # 🔥 Usa pydantic_ai para ejecutar el modelo
        response = await agent.run(body.content)
        text = str(response.output)
        msgs.append(Message(role="assistant", content=text))
        save_history({k: [m.model_dump() for m in v] for k, v in HISTORY.items()})
        yield text

    return StreamingResponse(token_generator(), media_type="text/plain")
