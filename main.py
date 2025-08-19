import time
import logging
from services.telegram_client import TelegramClient
from handlers.message_handlers import process_message
from config.settings import TELEGRAM_TOKEN
from database.db_manager import init_db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем логгер для main модуля
logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска бота"""
    # Инициализация базы данных
    init_db()
    
    # Создание Telegram клиента
    client = TelegramClient(TELEGRAM_TOKEN)
    
    logger.info("Бот запущен...")
    logger.info("Ожидание сообщений...")
    
    # Основной цикл бота
    while True:
        try:
            # Получение обновлений
            updates = client.get_updates()
            
            # Обработка каждого обновления
            for update in updates:
                response = process_message(update, client)
                
                if response:
                    # Отправка ответа
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    if chat_id:
                        client.send_message(chat_id, response)
            
            # Небольшая пауза между запросами
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("Бот остановлен.")
            break
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(5)  # Пауза при ошибке

if __name__ == "__main__":
    main() 