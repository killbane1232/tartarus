import random
import logging
from models import CharacterModel, GameStateModel, RoomModel, DungeonModel, StateChange, ExitModel
from services.ollama_service import ollama_with_validation
from config.settings import RACES, CLASSES, USE_OLLAMA

# Настройка логгера
logger = logging.getLogger(__name__)

def roll_hp(hit_die: int, con_mod: int) -> int:
    """Бросок здоровья персонажа"""
    return hit_die + con_mod

def generate_character(user_id: int, name: str) -> CharacterModel:
    """Генерация персонажа"""
    race = random.choice(RACES)
    cls = random.choice(list(CLASSES.keys()))
    con_mod = random.randint(0, 3)
    hp = roll_hp(CLASSES[cls]["hit_die"], con_mod)
    items = CLASSES[cls]["items"]

    char = CharacterModel(
        name=name,
        race=race,
        cls=cls,
        hp=hp,
        inventory=items,
        location="Room1"
    )
    return char

def create_default_dungeon() -> GameStateModel:
    """Создание подземелья по умолчанию"""
    # Создаем персонажа по умолчанию
    player = CharacterModel(
        name="Герой",
        race="Человек",
        cls="Воин",
        hp=15,
        inventory=["Меч", "Щит"],
        location="Room1"
    )
    
    # Создаем комнаты
    room1 = RoomModel(
        description="Каменная комната с факелами на стенах. Воздух пахнет пылью и древностью.",
        items=["Факел", "Ключ"],
        enemies=[],
        friendly_npcs=[],
        exits={
            "Room2": ExitModel(target_room="Room2", name="Деревянная дверь", is_hidden=False),
            "Room3": ExitModel(target_room="Room3", name="Секретный проход", is_hidden=True)
        }
    )
    
    room2 = RoomModel(
        description="Старая библиотека с высокими полками. Книги покрыты пылью.",
        items=["Старинная книга", "Свиток"],
        enemies=["Скелет"],
        friendly_npcs=["Мудрый библиотекарь"],
        exits={
            "Room1": ExitModel(target_room="Room1", name="Каменная арка", is_hidden=False),
            "Room3": ExitModel(target_room="Room3", name="Ржавая дверь", is_hidden=False)
        }
    )
    
    room3 = RoomModel(
        description="Темная камера с алтарем. В углу мерцает странный свет.",
        items=["Драгоценный камень"],
        enemies=[],
        friendly_npcs=[],
        exits={
            "Room2": ExitModel(target_room="Room2", name="Деревянная дверь", is_hidden=False),
            "Room1": ExitModel(target_room="Room1", name="Потайной ход", is_hidden=True)
        }
    )
    
    # Создаем подземелье
    dungeon = DungeonModel(
        rooms={
            "Room1": room1,
            "Room2": room2,
            "Room3": room3
        }
    )
    
    adventure_description = """Древние руины хранят множество тайн. Говорят, что в этих стенах спрятаны сокровища древних магов, но путь к ним охраняют нежить и ловушки. Ваша задача - исследовать подземелье и найти все его секреты."""
    
    return GameStateModel(
        player=player, 
        dungeon=dungeon,
        adventure_description=adventure_description,
        story_context="Вы стоите в древних руинах, готовые к приключению.",
        is_adventure_completed=False
    )

def generate_dungeon(adventure_prompt: str) -> GameStateModel:
    """Генерация подземелья"""
    if USE_OLLAMA:
        system_prompt = """Ты создаешь DnD приключения в формате JSON. 

ПРАВИЛА:
1. Первая комната (Room1) не должна содержать врагов
2. Создавай 2-3 комнаты с интересными описаниями
3. Добавляй 1-2 дружественных NPC для взаимодействия
4. Используй скрытые проходы (is_hidden: true) для исследования
5. Давай человекочитаемые имена выходам ("Ржавая дверь", "Секретный проход")
6. Все параметры в JSON обязательны, но массивы могут быть пустыми
7. Описание комнаты обязательно должно содержать все предметы, врагов и персонажей в этой комнате, но НЕ должна содержать скрытые проходы
8. Подземелье обязательно должно иметь конечную цель, по достижению которой приключение закончится и эта цель должна быть далеко от начальной локации.
9. Отвечай ТОЛЬКО в формате JSON, без дополнительного текста

СТРУКТУРА:
{
  "player": {
    "name": "Герой",
    "race": "Человек", 
    "cls": "Воин",
    "hp": 15,
    "inventory": ["Меч", "Щит"],
    "location": "Room1"
  },
  "dungeon": {
    "rooms": {
      "Room1": {
        "description": "Описание комнаты",
        "items": ["список предметов"],
        "enemies": [],
        "friendly_npcs": ["список NPC"],
        "exits": {
          "Room2": {
            "target_room": "Room2",
            "name": "Имя выхода",
            "is_hidden": false,
            "is_blocked": false
          }
        }
      }
    }
  },
  "adventure_description": "Описание приключения",
  "story_context": "Начальный контекст",
  "is_adventure_completed": false
}"""

        user_prompt = "Создай DnD приключение по указанной структуре."
        
        if adventure_prompt:
            user_prompt += f"\n\nПользователь хочет примерно такое описание приключения: {adventure_prompt}"
        
        logger.debug(f"[DEBUG] Длина системного промпта: {len(system_prompt)}")
        logger.debug(f"[DEBUG] Длина пользовательского промпта: {len(user_prompt)}")
        
        result = ollama_with_validation(user_prompt, GameStateModel, system_prompt=system_prompt)
        
        # Если Ollama не смог сгенерировать, используем подземелье по умолчанию
        if result is None:
            logger.warning("Ollama не смог сгенерировать подземелье, используем подземелье по умолчанию")
            return create_default_dungeon()
        
        return result
    else:
        logger.info("Используем подземелье по умолчанию (режим без Ollama)")
        return create_default_dungeon()

def apply_state_changes(state: GameStateModel, changes: StateChange) -> GameStateModel:
    """Применение изменений к состоянию игры"""
    # Создаем копию состояния
    try:
        new_state = state.model_copy(deep=True)
    except AttributeError:
        # Для старых версий Pydantic
        new_state = state.copy(deep=True)
    
    # Если действие игнорируется, просто добавляем описание
    if changes.ignore_action:
        new_state.last_action_description = changes.last_action_description or "Ничего не происходит."
        return new_state
    
    # Применяем изменения персонажа
    if changes.player_hp_change is not None:
        new_state.player.hp += changes.player_hp_change
        # Проверяем смерть персонажа
        if new_state.player.hp <= 0:
            new_state.is_adventure_completed = True
    
    if changes.player_location_change is not None:
        new_state.player.location = changes.player_location_change
    
    # Применяем изменения инвентаря
    if changes.inventory_add:
        for item in changes.inventory_add:
            if item not in new_state.player.inventory:
                new_state.player.inventory.append(item)
    
    if changes.inventory_remove:
        for item in changes.inventory_remove:
            if item in new_state.player.inventory:
                new_state.player.inventory.remove(item)
    
    # Применяем изменения текущей комнаты
    current_room = new_state.dungeon.rooms[new_state.player.location]
    
    if changes.room_items_add:
        for item in changes.room_items_add:
            if item not in current_room.items:
                current_room.items.append(item)
    
    if changes.room_items_remove:
        for item in changes.room_items_remove:
            if item in current_room.items:
                current_room.items.remove(item)
    
    if changes.room_enemies_add:
        for enemy in changes.room_enemies_add:
            if enemy not in current_room.enemies:
                current_room.enemies.append(enemy)
    
    if changes.room_enemies_remove:
        for enemy in changes.room_enemies_remove:
            if enemy in current_room.enemies:
                current_room.enemies.remove(enemy)
    
    # Применяем изменения описания комнаты
    if changes.room_description_change:
        current_room.description = changes.room_description_change
    
    # Применяем изменения дружественных NPC
    if changes.room_friendly_npcs_add:
        for npc in changes.room_friendly_npcs_add:
            if npc not in current_room.friendly_npcs:
                current_room.friendly_npcs.append(npc)
    
    if changes.room_friendly_npcs_remove:
        for npc in changes.room_friendly_npcs_remove:
            if npc in current_room.friendly_npcs:
                current_room.friendly_npcs.remove(npc)
    
    # Применяем изменения выходов
    if changes.room_exits_reveal:
        for exit_name in changes.room_exits_reveal:
            # Ищем выход по имени комнаты назначения
            for exit_key, exit_info in current_room.exits.items():
                if exit_info.target_room == exit_name:
                    current_room.exits[exit_key].is_hidden = False
                    break
    
    if changes.room_exits_hide:
        for exit_name in changes.room_exits_hide:
            # Ищем выход по имени комнаты назначения
            for exit_key, exit_info in current_room.exits.items():
                if exit_info.target_room == exit_name:
                    current_room.exits[exit_key].is_hidden = True
                    break
    
    if changes.room_exits_block:
        for exit_name in changes.room_exits_block:
            # Ищем выход по имени комнаты назначения
            for exit_key, exit_info in current_room.exits.items():
                if exit_info.target_room == exit_name:
                    current_room.exits[exit_key].is_blocked = True
                    break
    
    if changes.room_exits_unblock:
        for exit_name in changes.room_exits_unblock:
            # Ищем выход по имени комнаты назначения
            for exit_key, exit_info in current_room.exits.items():
                if exit_info.target_room == exit_name:
                    current_room.exits[exit_key].is_blocked = False
                    break
    
    # Применяем общие изменения
    if changes.is_adventure_completed is not None:
        new_state.is_adventure_completed = changes.is_adventure_completed
    
    if changes.last_action_description:
        new_state.last_action_description = changes.last_action_description
    
    return new_state

def process_player_action(state: GameStateModel, action: str) -> GameStateModel:
    """Обработка действий игрока"""
    if USE_OLLAMA:
        system_prompt = """Ты ведущий DnD. Обрабатываешь действия игрока и возвращаешь только ИЗМЕНЕНИЯ состояния в JSON.

ВАЖНЫЕ ПРАВИЛА:
1. Вместо изменения всего состояния игры, опиши только ИЗМЕНЕНИЯ в формате JSON.
2. Если игрок переходит в другую комнату и переходы НЕ заблокированы и НЕ скрыты - укажи player_location_change.
3. Если игрок подбирает предмет, добавь его в inventory_add и убери из room_items_remove.
4. Если игрок сражается, укажи player_hp_change (отрицательное значение для урона).
5. Если игрок умирает (hp <= 0), установи is_adventure_completed = true.
6. Если игрок достигает конечной цели приключения, установи is_adventure_completed = true.
7. Если игрок хочет взять/использовать предмет, которого НЕТ в игре - укажи player_hp_change = -5 и опиши падение балки.
8. Если игрок хочет использовать невозможное свойство предмета - опиши неудачную попытку.
9. КРИТИЧЕСКОЕ ПРАВИЛО: Если игрок описывает действие, которое происходит САМО ПО СЕБЕ, или действие, которое делает НЕ ЕГО персонаж, или действие, которое физически невозможно - установи ignore_action = true.

ПРАВИЛА ВЗАИМОДЕЙСТВИЯ С NPC:
10. Если игрок разговаривает с дружественным NPC - создай интересный диалог и возможные изменения.
11. Если игрок торгуется с NPC - NPC может предложить обмен предметами.
12. NPC могут давать подсказки, квесты или полезные предметы.
13. Если игрок оскорбляет NPC - NPC может стать враждебным (добавить в enemies, убрать из friendly_npcs).

ПРАВИЛА ИЗМЕНЕНИЯ ОКРУЖЕНИЯ:
14. Если игрок изменяет комнату (ломает что-то, зажигает факелы, открывает секретные проходы) - измени room_description_change, но не теряй то, что в ней было, но не изменилось.
15. Изменения должны быть логичными и соответствовать действиям игрока.

ПРАВИЛА СКРЫТЫХ ПРОХОДОВ:
16. Выходы имеют человекочитаемые имена (например "Ржавая дверь", "Секретный проход").
17. Скрытые проходы (is_hidden=true) не показываются игроку, но существуют.
18. Если игрок находит скрытый проход (осматривает стену, нажимает на камень) - используй room_exits_reveal.
19. Игрок НЕ МОЖЕТ создавать новые проходы - только находить существующие.

ПРАВИЛА БОЯ И БЛОКИРОВКИ ВЫХОДОВ:
20. Если в комнате есть враги и игрок пытается уйти - враги могут блокировать выходы (room_exits_block).
21. При попытке сбежать из боя - враги наносят урон (player_hp_change отрицательное).
22. Блокировка снимается только после победы над всеми врагами (room_exits_unblock).

СТРУКТУРА ОТВЕТА:
{
  "player_hp_change": 0,
  "player_location_change": null,
  "inventory_add": [],
  "inventory_remove": [],
  "room_items_add": [],
  "room_items_remove": [],
  "room_enemies_add": [],
  "room_enemies_remove": [],
  "room_description_change": null,
  "room_friendly_npcs_add": [],
  "room_friendly_npcs_remove": [],
  "room_exits_reveal": [],
  "room_exits_hide": [],
  "room_exits_block": [],
  "room_exits_unblock": [],
  "is_adventure_completed": false,
  "last_action_description": "Описание действия",
  "ignore_action": false
}

Отвечай ТОЛЬКО в формате JSON, без дополнительного текста."""

        user_prompt = f"""Действие игрока: "{action}"

Текущее состояние игры:
{state.json(ensure_ascii=False)}"""
        
        logger.debug(f"[DEBUG] Длина системного промпта: {len(system_prompt)}")
        logger.debug(f"[DEBUG] Длина пользовательского промпта: {len(user_prompt)}")
        
        result = ollama_with_validation(user_prompt, StateChange, system_prompt=system_prompt)
        logger.debug(f"[DEBUG] Результат: {result}")
        # Если Ollama не смог обработать действие, возвращаем исходное состояние
        if result is None:
            logger.warning(f"Ollama не смог обработать действие: {action}")
            # Создаем простое изменение состояния для отладки
            changes = StateChange(
                last_action_description=f"Действие '{action}' не было обработано.",
                ignore_action=True
            )
            return apply_state_changes(state, changes)
        
        # Проверяем, что результат является StateChange
        if not isinstance(result, StateChange):
            logger.error(f"Ollama вернул некорректный тип данных: {type(result)}")
            changes = StateChange(
                last_action_description=f"Ошибка обработки действия '{action}'.",
                ignore_action=True
            )
            return apply_state_changes(state, changes)
        
        # Применяем изменения к состоянию
        return apply_state_changes(state, result)
    else:
        logger.info(f"Ollama отключен, действие не обработано: {action}")
        # Создаем простое изменение состояния для отладки
        changes = StateChange(
            last_action_description=f"Действие '{action}' не обработано (Ollama отключен).",
            ignore_action=True
        )
        return apply_state_changes(state, changes) 