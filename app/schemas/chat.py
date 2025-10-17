from __future__ import annotations
from pydantic import BaseModel
from typing import Literal

# Roles posibles en la conversación
Role = Literal["user", "assistant", "system"]


class Message(BaseModel):
    """Representa un mensaje de la conversación."""
    role: Role
    content: str


class ChatIn(BaseModel):
    """Entrada del usuario (lo que se envía desde el frontend)."""
    content: str
