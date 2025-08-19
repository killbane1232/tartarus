from typing import List, Dict
from pydantic import BaseModel
from .exit_model import ExitModel

class RoomModel(BaseModel):
    description: str
    items: List[str]
    enemies: List[str]
    friendly_npcs: List[str] = []  # Дружественные NPC в комнате
    exits: Dict[str, ExitModel]  # Словарь выходов с их описаниями 