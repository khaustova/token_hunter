import logging
from core.celery import app

logger = logging.getLogger(__name__)


def get_active_tasks() -> list:
    """Returns a list of all active Celery tasks in the system.
    
    Note:
        Only returns tasks from the first available worker.
        May return an empty list if no active tasks exist.

    Returns:
        List of dictionaries containing active task data.
    """
    insp = app.control.inspect()
    active_tasks = insp.active()
    worker = list(active_tasks.keys())[0]

    return active_tasks[worker]


def get_dexscreener_worker_tasks_ids() -> dict | None:
    """Retrieves IDs of all active tasks categorized by type.
    
    Task categories:
    - parsing_task_id: Top traders parsing tasks.
    - track_tokens_task_id: Purchased token tracking tasks.
    - filter_task_id: Token filter monitoring tasks.
    - boosted_task_id: Boosted tokens monitoring tasks.
    - latest_task_id: Recently added tokens monitoring tasks.

    Returns:
        Dictionary with task IDs categorized by type:
            {
                "parsing_task_id": list[str],
                "track_tokens_task_id": list[str],
                "filter_task_id": list[str],
                "boosted_task_id": list[str],
                "latest_task_id": list[str]
            }
        Returns None if an error occurs.
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
