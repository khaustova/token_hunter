import logging
from core.celery import app

logger = logging.getLogger(__name__)


def get_active_tasks() -> list:
    """Возвращает список всех активных задач Celery в системе.
    
    Note:
        Возвращает задачи только от первого доступного воркера.
        Если активных задач нет, может вернуть пустой список.

    Returns:
        Список словарей с данными об активных задачах
    """
    insp = app.control.inspect()
    active_tasks = insp.active()
    worker = list(active_tasks.keys())[0]

    return active_tasks[worker]


def get_dexscreener_worker_tasks_ids() -> dict | None:
    """Получает ID всех активных задач.
    
    Классифицирует задачи по типам:
    - parsing_task_id: задачи парсинга топовых трейдеров
    - track_tokens_task_id: задачи отслеживания стоимости купленных токенов
    - filter_task_id: задачи мониторинга токенов по фильтру
    - boosted_task_id: задачи мониторинга забустенных токенов

    Returns:
        Словарь с ID задач по типам в формате:
            {
                "parsing_task_id": list[str],
                "track_tokens_task_id": list[str],
                "filter_task_id": list[str],
                "boosted_task_id": list[str],
                "latest_task_id": list[str]
            }
            или None в случае ошибки.
    """
    try:
        active_tasks = get_active_tasks()
        tasks_ids = {
            "parsing_task_id": [], 
            "track_tokens_task_id": [],
            "filter_task_id": [], 
            "boosted_task_id": [],
            "latest_task_id": []
        }
        for task in active_tasks:
            if task["name"] == "token_hunter.src.dex.tasks.monitor_filtered_tokens_task":
                tasks_ids["filter_task_id"].append(task["id"])
            elif task["name"] == "token_hunter.src.dex.tasks.monitor_boosted_tokens_task":
                tasks_ids["boosted_task_id"].append(task["id"])
            elif task["name"] == "token_hunter.src.dex.tasks.monitor_latest_tokens_task":
                tasks_ids["latest_task_id"].append(task["id"])
            elif task["name"] == "token_hunter.src.dex.tasks.parse_top_traders_task":
                tasks_ids["parsing_task_id"].append(task["id"])
            elif task["name"] == "token_hunter.src.token.tasks.track_tokens_task":
                tasks_ids["track_tokens_task_id"].append(task["id"])
        return tasks_ids
    except Exception:
        return tasks_ids
