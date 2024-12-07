import httpx
import time
import logging
import requests
from datetime import datetime
from httpx._config import Timeout
from core.celery import app

logger = logging.getLogger(__name__)


def get_active_tasks() -> list:
    """
    Возвращает все запущенные задачи Celery.
    """
    
    insp = app.control.inspect()
    active_tasks = insp.active()
    worker = list(active_tasks.keys())[0]
    
    return active_tasks[worker]


def get_dexscreener_worker_tasks_ids() -> dict | None:
    """
    Возвращает информацию о запущенных задачах мониторинга и парсинга данных.
    """
    
    try:
        active_tasks = get_active_tasks()
        tasks_ids = {"parsing_task_id": None, "watching_task_id": None}
        for task in active_tasks:
            if task["name"] == "token_hunter.src.dex.tasks.watching_dexscreener_task":
                tasks_ids["watching_task_id"] = task["id"]
                break
            elif task["name"] == "token_hunter.src.dex.tasks.parsing_dexscreener_task":
                tasks_ids["parsing_task_id"] = task["id"]
                break
        return tasks_ids
    except:   
        return tasks_ids
    

def get_token_data(pairs: str | list[str]) -> dict:
    """
    Возвращает данные о токена или списке токенов с DexScreener.
    """
    
    token_data_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pairs}"
    token_data = None
    while not token_data:
        try:
            token_data = requests.get(token_data_url).json()["pairs"]
            #token_data = httpx.get(token_data_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
        except:
            logger.debug(f"Не удалось получить данные через API. Повтор попытки")
            time.sleep(1)
            continue
        
    return token_data


def get_token_age(created_date: datetime) -> str:
    """
    Возвращает текущий возраст токена.
    """
    
    now_date = datetime.now()
    created_date = datetime.fromtimestamp(created_date / 1000)
    token_age = (now_date - created_date).total_seconds() / 60
    token_age = round(token_age, 2)
    
    return token_age


def get_pairs_count(token_address):
    try:
        pairs = requests.get("https://api.dexscreener.com/latest/dex/tokens/" + token_address).json()["pairs"]
        count = len(pairs)
    except:
        count = 0
        
    return count
