import requests
import json
import logging
from typing import Optional, Dict, Any
from config.settings import TELEGRAM_TOKEN

# Настройка логгера
logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
    
    def get_updates(self) -> list:
        """Получение обновлений от Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {
            "offset": self.offset,
            "timeout": 30
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok") and data.get("result"):
                updates = data["result"]
                if updates:
                    self.offset = updates[-1]["update_id"] + 1
                return updates
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def send_message(self, chat_id: int, text: str) -> bool:
        """Отправка сообщения"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json().get("ok", False)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def set_webhook(self, url: str) -> bool:
        """Установка webhook (для продакшена)"""
        webhook_url = f"{self.base_url}/setWebhook"
        data = {"url": url}
        
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status()
            return response.json().get("ok", False)
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False 