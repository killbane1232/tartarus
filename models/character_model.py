from typing import List
from pydantic import BaseModel

class CharacterModel(BaseModel):
    name: str
    race: str
    cls: str
    hp: int
    inventory: List[str]
    location: str 