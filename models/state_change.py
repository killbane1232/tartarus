from typing import List, Optional
from pydantic import BaseModel

class StateChange(BaseModel):
    """Модель для описания изменений состояния игры"""
    # Изменения персонажа
    player_hp_change: Optional[int] = None  # Изменение HP (может быть отрицательным)
    player_location_change: Optional[str] = None  # Новое местоположение
    inventory_add: Optional[List[str]] = None  # Предметы для добавления
    inventory_remove: Optional[List[str]] = None  # Предметы для удаления
    
    # Изменения комнаты
    room_items_add: Optional[List[str]] = None  # Предметы для добавления в комнату
    room_items_remove: Optional[List[str]] = None  # Предметы для удаления из комнаты
    room_enemies_add: Optional[List[str]] = None  # Враги для добавления
    room_enemies_remove: Optional[List[str]] = None  # Враги для удаления
    room_description_change: Optional[str] = None  # Новое описание комнаты
    room_friendly_npcs_add: Optional[List[str]] = None  # Дружественные NPC для добавления
    room_friendly_npcs_remove: Optional[List[str]] = None  # Дружественные NPC для удаления
    
    # Изменения выходов
    room_exits_reveal: Optional[List[str]] = None  # Скрытые выходы для раскрытия
    room_exits_hide: Optional[List[str]] = None  # Выходы для скрытия
    room_exits_block: Optional[List[str]] = None  # Выходы для блокировки
    room_exits_unblock: Optional[List[str]] = None  # Выходы для разблокировки
    
    # Общие изменения
    is_adventure_completed: Optional[bool] = None  # Завершение приключения
    last_action_description: Optional[str] = None  # Описание действия
    
    # Флаг для игнорирования действия
    ignore_action: bool = False  # Если True, действие игнорируется 