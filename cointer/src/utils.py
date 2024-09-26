import httpx
import time
import logging
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


def get_dexscreener_worker_tasks_ids() -> str | None:
    try:
        active_tasks = get_active_tasks()
        print(active_tasks)
        tasks_ids = {"parsing_task_id": None, "watching_task_id": None}
        for task in active_tasks:
            if task["name"] == "cointer.src.dex_tasks.watching_dexscreener_task":
                tasks_ids["watching_task_id"] = task["id"]
                break
            elif task["name"] == "cointer.src.dex_tasks.parsing_dexscreener_task":
                tasks_ids["parsing_task_id"] = task["id"]
                break
        return tasks_ids
    except:   
        return tasks_ids
    

def get_coins_prices(pairs: str | list[str]) -> dict:
    coin_prices_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pairs}"
    coin_prices = None
    while not coin_prices:
        time.sleep(1)
        try:
            coin_prices = httpx.get(coin_prices_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
        except:
            continue
        
    return coin_prices


def get_coin_age(created_date: datetime) -> str:
    now_date = datetime.now()
    created_date = datetime.fromtimestamp(created_date / 1000)
    coin_age = (now_date - created_date).total_seconds() / 60
    
    return coin_age
