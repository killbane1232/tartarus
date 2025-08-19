# ======== CONFIG ========
TELEGRAM_TOKEN = "YOUR_TOKEN"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "gpt-oss:20b"
#OLLAMA_MODEL = "qwen3:8b"
USE_OLLAMA = True

# DnD Game Constants
RACES = ["Человек", "Эльф", "Дварф", "Тифлинг", "Полурослик"]
CLASSES = {
    "Воин": {"hit_die": 10, "items": ["Меч", "Щит", "Кольчуга"]},
    "Маг": {"hit_die": 6, "items": ["Посох", "Книга заклинаний", "Мантия"]},
    "Разбойник": {"hit_die": 8, "items": ["Кинжал", "Лёгкий арбалет", "Кожаная броня"]},
    "Жрец": {"hit_die": 8, "items": ["Булава", "Священный символ", "Кольчуга"]}
} 