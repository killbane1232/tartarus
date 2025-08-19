from telegram import Update
from telegram.ext import CallbackContext
from services.dnd_service import generate_character, generate_dungeon, process_player_action
from database.db_manager import save_state, load_state

def start_cmd(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    update.message.reply_text("🎲 Привет! Я DnD бот.\n\nКоманды:\n/new [описание приключения] — начать новую игру\n/character [имя] — создать персонажа\n/status — показать статус\n/story — история приключения\n\nПросто пишите действия на русском языке!")

def new_game_cmd(update: Update, context: CallbackContext):
    """Обработчик команды /new"""
    dungeon = generate_dungeon()
    if dungeon:
        save_state(update.effective_user.id, dungeon)
        update.message.reply_text("Новая игра начата!")
    else:
        update.message.reply_text("Ошибка генерации подземелья.")

def character_cmd(update: Update, context: CallbackContext):
    """Обработчик команды /character"""
    parts = update.message.text.split(maxsplit=1)
    name = parts[1] if len(parts) > 1 else "Герой"
    char = generate_character(update.effective_user.id, name)
    state = load_state(update.effective_user.id)
    if state:
        state.player = char
        save_state(update.effective_user.id, state)
        update.message.reply_text(f"Персонаж {char.name} создан!")
    else:
        update.message.reply_text("Сначала начните игру: /new")

def player_action(update: Update, context: CallbackContext):
    """Обработчик действий игрока"""
    state = load_state(update.effective_user.id)
    if not state:
        update.message.reply_text("Сначала начните игру: /new")
        return

    updated_state = process_player_action(state, update.message.text)
    if updated_state:
        save_state(update.effective_user.id, updated_state)
        update.message.reply_text("Действие выполнено!")
    else:
        update.message.reply_text("Ошибка обработки действия.") 