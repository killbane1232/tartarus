import sqlite3
from typing import Optional
from models import GameStateModel

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect("dnd.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            user_id INTEGER PRIMARY KEY,
            state_json TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_state(user_id: int, state: GameStateModel):
    """Сохранение состояния игры пользователя"""
    conn = sqlite3.connect("dnd.db")
    c = conn.cursor()
    c.execute("REPLACE INTO game_state (user_id, state_json) VALUES (?, ?)",
              (user_id, state.json(ensure_ascii=False)))
    conn.commit()
    conn.close()

def load_state(user_id: int) -> Optional[GameStateModel]:
    """Загрузка состояния игры пользователя"""
    conn = sqlite3.connect("dnd.db")
    c = conn.cursor()
    c.execute("SELECT state_json FROM game_state WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return GameStateModel.parse_raw(row[0])
    return None 