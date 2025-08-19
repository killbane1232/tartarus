from typing import Dict
from pydantic import BaseModel
from .room_model import RoomModel

class DungeonModel(BaseModel):
    rooms: Dict[str, RoomModel] 