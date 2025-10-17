import json
import os
from typing import Dict, List, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
FILE_PATH = os.path.join(DATA_DIR, "chat_history.json")


def ensure_data_dir() -> None:
    """Crea el directorio /data si no existe."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_history() -> Dict[str, List[Dict[str, Any]]]:
    """Carga el historial desde chat_history.json. Si no existe, devuelve {}."""
    ensure_data_dir()
    if not os.path.exists(FILE_PATH):
        return {}
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Si el archivo está corrupto, lo reiniciamos
        return {}


def save_history(history: Dict[str, List[Dict[str, Any]]]) -> None:
    """Guarda el historial completo en chat_history.json."""
    ensure_data_dir()
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
