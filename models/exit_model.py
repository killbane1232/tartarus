from pydantic import BaseModel

class ExitModel(BaseModel):
    """Модель выхода из комнаты"""
    target_room: str  # Комната назначения
    name: str  # Человекочитаемое имя (например "Ржавая дверь")
    is_hidden: bool = False  # Скрытый проход
    is_blocked: bool = False  # Заблокирован ли выход 