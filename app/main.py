from __future__ import annotations
import os
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from app.schemas.chat import Message, ChatIn
from app.utils.storage import load_history, save_history
from app.agents.briggie_mistral import stream_mistral  # ✅ import correcto

# ==== CONFIGURACIÓN ====
load_dotenv()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")

app = FastAPI(title="Briggie Mistral Online")

# ==== CORS ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:5500", "http://127.0.0.1:5500", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== HISTORIAL EN MEMORIA (SIN SQL) ====
HISTORY: Dict[str, List[Message]] = {}
raw_data = load_history()
for user_id, msgs in raw_data.items():
    HISTORY[user_id] = [Message(**m) for m in msgs]


def _ensure_user(user_id: str) -> List[Message]:
    """Asegura que el usuario tenga un historial inicializado."""
    if user_id not in HISTORY:
        HISTORY[user_id] = []
    return HISTORY[user_id]


# ==== ENDPOINTS ====

@app.get("/health")
async def health():
    """Devuelve el estado del backend y el modelo activo."""
    return {
        "status": "ok",
        "provider": f"mistral:{os.getenv('MISTRAL_MODEL', 'mistral-small-latest')}",
        "mode": "online",
    }


@app.get("/chat-system/chat/{user_id}")
async def get_chat(user_id: str):
    """Devuelve el historial completo del usuario."""
    return _ensure_user(user_id)


@app.post("/chat-system/chat/{user_id}")
async def post_chat(user_id: str, body: ChatIn):
    """Guarda un nuevo mensaje del usuario y actualiza el JSON."""
    msgs = _ensure_user(user_id)
    msg = Message(role="user", content=body.content)
    msgs.append(msg)
    save_history({k: [m.model_dump() for m in v] for k, v in HISTORY.items()})
    return {"role": "user", "content": body.content}


@app.post("/chat-system/chat-streaming/{user_id}")
async def chat_stream(user_id: str, body: ChatIn):
    """
    Envía el mensaje del usuario al modelo Mistral (API Online),
    recibe la respuesta por streaming y la guarda en el JSON.
    """
    msgs = _ensure_user(user_id)
    system_prompt = Message(
        role="system",
        content=(
            "You are Briggie, a compassionate medical assistant speaking fluent English. "
            "Be empathetic, clear, and informative. "
            "Always explain medical concepts simply and encourage professional consultation when necessary."
        ),
    )
    full_messages = [system_prompt] + msgs + [Message(role="user", content=body.content)]

    async def token_generator():
        assistant_text = ""
        async for delta in stream_mistral(full_messages):
            assistant_text += delta
            yield delta
        msgs.append(Message(role="assistant", content=assistant_text))
        save_history({k: [m.model_dump() for m in v] for k, v in HISTORY.items()})

    return StreamingResponse(token_generator(), media_type="text/plain")
