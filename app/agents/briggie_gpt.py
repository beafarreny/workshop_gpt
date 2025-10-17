from pydantic_ai import Agent
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

agent = Agent(
    name="briggie_gpt",
    model=f"openai:{OPENAI_MODEL}",   # 🔥 el prefijo 'openai:' ya usa la API key del entorno
    system_prompt=(
        "You are Briggie, a warm, empathetic English-speaking medical companion. "
        "Always be concise, kind, and explain health information in simple terms. "
        "Never give diagnoses; instead, suggest possible explanations and encourage "
        "users to consult a healthcare professional when appropriate."
    ),
)
