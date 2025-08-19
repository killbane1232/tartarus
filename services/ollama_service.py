import json
import logging
import requests
from typing import TypeVar, Generic
from pydantic import ValidationError
from config.settings import OLLAMA_URL, OLLAMA_MODEL

# Настройка логгера
logger = logging.getLogger(__name__)

T = TypeVar('T')

def check_ollama_server() -> bool:
    """Проверка доступности Ollama сервера"""
    try:
        # Проверяем доступность сервера
        health_url = OLLAMA_URL.replace("/api/chat", "/api/tags")
        response = requests.get(health_url, timeout=900)
        return response.status_code == 200
    except:
        return False

def ollama_with_validation(prompt: str, schema_model: Generic[T], retries: int = 3, system_prompt: str = None) -> T:
    """Отправка запроса к Ollama с валидацией ответа"""
    
    # Проверяем, что промпт не пустой
    if not prompt or not prompt.strip():
        logger.warning("[Ollama] Пустой промпт")
        return None
    
    # Проверяем доступность сервера
    if not check_ollama_server():
        logger.error(f"[Ollama] Сервер недоступен по адресу {OLLAMA_URL}")
        return None

    for attempt in range(retries):
        messages = []
        
        # Добавляем системный промпт, если он есть
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Добавляем пользовательский промпт
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }
        try:
            logger.info(f"[Ollama] Отправка запроса к модели {OLLAMA_MODEL}...")
            logger.debug(f"[Ollama] Промпт: {prompt[:200]}...")
            # Увеличиваем таймаут до 60 секунд
            resp = requests.post(OLLAMA_URL, json=payload, timeout=1800)
            resp.raise_for_status()
            
            response_data = resp.json()
            if "message" not in response_data or "content" not in response_data["message"]:
                logger.warning(f"[Attempt {attempt+1}] Неожиданный формат ответа от Ollama")
                continue
                
            content = response_data["message"]["content"]
            logger.info(f"[Ollama] Получен ответ длиной {len(content)} символов")
            
            # Очищаем контент от лишних символов
            content = content.strip()
            if not content:
                logger.warning(f"[Attempt {attempt+1}] Пустой ответ от Ollama")
                continue
            
            # Проверяем на простые ответы типа "Okay" или "the user sent"
            if any(simple_response in content.lower() for simple_response in ["okay", "the user sent", "empty message", "just the word"]):
                logger.warning(f"[Attempt {attempt+1}] Ollama вернул простой ответ вместо JSON: {content}")
                continue
            
            # Пытаемся найти JSON в ответе
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning(f"[Attempt {attempt+1}] JSON не найден в ответе: {content[:100]}...")
                continue
            
            json_content = content[json_start:json_end]
            logger.debug(f"[Ollama] Извлечен JSON: {json_content[:100]}...")
            
            # Пытаемся распарсить JSON
            data = json.loads(json_content)
            validated = schema_model.parse_obj(data)
            logger.info(f"[Ollama] Успешная валидация данных")
            return validated
            
        except json.JSONDecodeError as e:
            logger.error(f"[Attempt {attempt+1}] JSON decode error: {e}")
            logger.debug(f"[Ollama] Содержимое ответа: {content[:200]}...")
            continue
        except ValidationError as e:
            logger.error(f"[Attempt {attempt+1}] Validation error: {e}")
            continue
        except KeyError as e:
            logger.error(f"[Attempt {attempt+1}] Key error: {e}")
            continue
        except requests.exceptions.Timeout as e:
            logger.error(f"[Attempt {attempt+1}] Timeout error: {e}")
            continue
        except requests.RequestException as e:
            logger.error(f"[Ollama] Request failed: {e}")
            break
        except Exception as e:
            logger.error(f"[Attempt {attempt+1}] Unexpected error: {e}")
            continue
    
    logger.error(f"[Ollama] Все попытки исчерпаны, возвращаем None")
    return None 