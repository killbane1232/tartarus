from services.dnd_service import generate_character, generate_dungeon, process_player_action
from database.db_manager import save_state, load_state

def get_room_description(state):
    """Получение описания текущей комнаты"""
    current_room = state.dungeon.rooms[state.player.location]
    description = f"📍 {current_room.description}\n\n"
    
    if current_room.items:
        description += f"📦 Предметы: {', '.join(current_room.items)}\n"
    
    if current_room.enemies:
        description += f"⚔️ Враги: {', '.join(current_room.enemies)}\n"
    
    if current_room.friendly_npcs:
        description += f"👥 Дружественные NPC: {', '.join(current_room.friendly_npcs)}\n"
    
    # Отображаем только видимые и не заблокированные выходы
    visible_exits = []
    for exit_name, exit_info in current_room.exits.items():
        if not exit_info.is_hidden and not exit_info.is_blocked:
            visible_exits.append(exit_info.name)
    
    if visible_exits:
        description += f"🚪 Выходы: {', '.join(visible_exits)}\n"
    
    return description

def get_player_status(state):
    """Получение статуса игрока"""
    return f"👤 {state.player.name} ({state.player.race} {state.player.cls})\n❤️ HP: {state.player.hp}\n🎒 Инвентарь: {', '.join(state.player.inventory)}"

def get_adventure_info(state):
    """Получение информации о приключении"""
    info = ""
    if state.adventure_description:
        info += f"📖 {state.adventure_description}\n\n"
    if state.story_context:
        info += f"🎭 {state.story_context}\n\n"
    return info

def handle_start_command(chat_id: int, telegram_client) -> str:
    """Обработчик команды /start"""
    return "🎲 Привет! Я DnD бот.\n\nКоманды:\n/new [описание приключения] — начать новую игру\n/character [имя] — создать персонажа\n/status — показать статус\n/story — история приключения\n\nПросто пишите действия на русском языке!"

def handle_new_game_command(chat_id: int, adventure_prompt: str, telegram_client) -> str:
    """Обработчик команды /new"""
    dungeon = generate_dungeon(adventure_prompt)
    if dungeon:
        save_state(chat_id, dungeon)
        adventure_info = get_adventure_info(dungeon)
        status = get_player_status(dungeon)
        room_desc = get_room_description(dungeon)
        return f"🎮 Новая игра начата!\n\n{adventure_info}{status}\n\n{room_desc}"
    else:
        return "❌ Ошибка генерации подземелья."

def handle_character_command(chat_id: int, text: str, telegram_client) -> str:
    """Обработчик команды /character"""
    parts = text.split(maxsplit=1)
    name = parts[1] if len(parts) > 1 else "Герой"
    char = generate_character(chat_id, name)
    state = load_state(chat_id)
    if state:
        state.player = char
        save_state(chat_id, state)
        adventure_info = get_adventure_info(state)
        status = get_player_status(state)
        room_desc = get_room_description(state)
        return f"✨ Персонаж {char.name} создан!\n\n{adventure_info}{status}\n\n{room_desc}"
    else:
        return "❌ Сначала начните игру: /new"

def handle_status_command(chat_id: int, telegram_client) -> str:
    """Обработчик команды /status"""
    state = load_state(chat_id)
    if state:
        adventure_info = get_adventure_info(state)
        status = get_player_status(state)
        
        # Проверяем статус завершения
        if state.is_adventure_completed:
            if state.player.hp <= 0:
                completion_status = "💀 ИГРА ОКОНЧЕНА - Персонаж погиб"
            else:
                completion_status = "🏆 ПРИКЛЮЧЕНИЕ ЗАВЕРШЕНО - Победа!"
            
            return f"📊 Статус игры:\n\n{adventure_info}{status}\n\n{completion_status}\n\n🎮 Начните новую игру командой /new [описание приключения]"
        else:
            room_desc = get_room_description(state)
            return f"📊 Статус игры:\n\n{adventure_info}{status}\n\n{room_desc}"
    else:
        return "❌ Сначала начните игру: /new"

def handle_story_command(chat_id: int, telegram_client) -> str:
    """Обработчик команды /story"""
    state = load_state(chat_id)
    if state:
        story = "📚 История приключения:\n\n"
        
        if state.adventure_description:
            story += f"🎯 Цель приключения:\n{state.adventure_description}\n\n"
        
        if state.story_context:
            story += f"🎭 Текущий контекст:\n{state.story_context}\n\n"
        
        if state.last_action_description:
            story += f"📝 Последнее действие:\n{state.last_action_description}\n\n"
        
        story += f"📍 Текущее местоположение: {state.player.location}"
        
        # Добавляем информацию о завершении
        if state.is_adventure_completed:
            if state.player.hp <= 0:
                story += "\n\n💀 ИГРА ОКОНЧЕНА - Персонаж погиб"
            else:
                story += "\n\n🏆 ПРИКЛЮЧЕНИЕ ЗАВЕРШЕНО - Победа!"
            
            story += "\n\n🎮 Начните новую игру командой /new [описание приключения]"
        
        return story
    else:
        return "❌ Сначала начните игру: /new"

def handle_player_action(chat_id: int, text: str, telegram_client) -> str:
    """Обработчик действий игрока"""
    state = load_state(chat_id)
    if not state:
        return "❌ Сначала начните игру: /new"

    updated_state = process_player_action(state, text)
    if updated_state:
        save_state(chat_id, updated_state)
        
        # Формируем ответ
        response = f"🎯 Действие: {text}\n\n"
        
        # Добавляем описание действия, если есть
        if updated_state.last_action_description:
            response += f"📝 {updated_state.last_action_description}\n\n"
        
        # Проверяем завершение приключения
        if updated_state.is_adventure_completed:
            if updated_state.player.hp <= 0:
                response += "💀 ИГРА ОКОНЧЕНА! Ваш персонаж погиб.\n\n"
            else:
                response += "🏆 ПРИКЛЮЧЕНИЕ ЗАВЕРШЕНО! Поздравляем с победой!\n\n"
            
            response += "🎮 Начните новую игру командой /new [описание приключения]"
            return response
        
        response += get_player_status(updated_state) + "\n\n"
        response += get_room_description(updated_state)
        
        return response
    else:
        return "❌ Ошибка обработки действия."

def process_message(update: dict, telegram_client) -> str:
    """Основной обработчик сообщений"""
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    
    if not chat_id or not text:
        return ""
    
    # Обработка команд
    if text.startswith("/start"):
        return handle_start_command(chat_id, telegram_client)
    elif text.startswith("/new"):
        if len(text) < 5 or text[5:].strip() == "":
            return handle_new_game_command(chat_id, None, telegram_client)
        else:
            return handle_new_game_command(chat_id, text[5:].strip(), telegram_client)
    elif text.startswith("/character"):
        return handle_character_command(chat_id, text, telegram_client)
    elif text.startswith("/status"):
        return handle_status_command(chat_id, telegram_client)
    elif text.startswith("/story"):
        return handle_story_command(chat_id, telegram_client)
    else:
        return handle_player_action(chat_id, text, telegram_client) 