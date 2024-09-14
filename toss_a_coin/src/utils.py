import pandas as pd
import httpx
import time
import logging
from httpx._config import Timeout
from asgiref.sync import sync_to_async
from core.celery import app
from django.contrib.admin.models import LogEntry, ADDITION
from bs4 import BeautifulSoup
from toss_a_coin.models import TopTrader
from ..models import TopTrader

logger = logging.getLogger(__name__)

def get_active_tasks() -> list:
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
            if task["name"] == "toss_a_coin.src.dex_tasks.watching_dexscreener_task":
                tasks_ids["watching_task_id"] = task["id"]
                break
            elif task["name"] == "toss_a_coin.src.dex_tasks.parsing_dexscreener_task":
                tasks_ids["parsing_task_id"] = task["id"]
                break
        print(tasks_ids)
        return tasks_ids
    except:   
        return tasks_ids
    

def get_coins_prices(coins: str | list[str]) -> dict:
    coin_prices_url = f"https://api.dexscreener.com/latest/dex/tokens/{coins}"
    coin_prices = httpx.get(coin_prices_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
    
    print(coin_prices)
    
    if coin_prices:
        return coin_prices

    print(coin_prices)
    
    time.sleep(0.5)
    get_coins_prices(coins)
