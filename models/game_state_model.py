from typing import Optional
from pydantic import BaseModel
from .character_model import CharacterModel
from .dungeon_model import DungeonModel

class GameStateModel(BaseModel):
    player: CharacterModel
    dungeon: DungeonModel
    # Новые поля для описаний
    adventure_description: Optional[str] = None
    last_action_description: Optional[str] = None
    story_context: Optional[str] = None
    # Флаг завершения приключения
    is_adventure_completed: bool = False 