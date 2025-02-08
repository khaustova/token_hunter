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
            "parsing_task_id": [], 
            "track_tokens_task_id": [],
            "filter_task_id": [], 
            "boosted_task_id": [],
        }
        for task in active_tasks:
            if task["name"] == "token_hunter.src.dex.tasks.monitor_dexscreener_task":
                tasks_ids["filter_task_id"].append(task["id"])
            elif task["name"] == "token_hunter.src.dex.tasks.monitor_boosted_tokens_task":
                tasks_ids["boosted_task_id"].append(task["id"])
            elif task["name"] == "token_hunter.src.dex.tasks.parsing_dexscreener_task":
                tasks_ids["parsing_task_id"].append(task["id"])
            elif task["name"] == "token_hunter.src.token.tasks.track_tokens_task":
                tasks_ids["track_tokens_task_id"].append(task["id"])
        print(tasks_ids)
        return tasks_ids
    except:   
        return tasks_ids