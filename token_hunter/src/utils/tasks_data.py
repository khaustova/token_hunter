import logging
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
        tasks_ids = {
            "parsing_task_id": None, 
            "watching_task_id": None, 
            "boosted_task_id": None
        }
        for task in active_tasks:
            if task["name"] == "token_hunter.src.dex.tasks.watching_dexscreener_task":
                tasks_ids["watching_task_id"] = task["id"]
                break
            elif task["name"] == "token_hunter.src.dex.tasks.parsing_dexscreener_task":
                tasks_ids["parsing_task_id"] = task["id"]
                break
            elif task["name"] == "token_hunter.src.dex.tasks.watching_boosted_tokens_task":
                tasks_ids["boosted_task_id"] = task["id"]
                break
        return tasks_ids
    except:   
        return tasks_ids