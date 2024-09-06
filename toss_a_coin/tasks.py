from asgiref.sync import async_to_sync
from .dexscreener_worker import run_dexscreener_watcher
from core.celery import app
from celery.contrib.abortable import AbortableTask

@app.task(bind=True, base=AbortableTask)
def watch_dexscreener_task(self, filter: str) -> str:
    async_to_sync(run_dexscreener_watcher)(filter)
    
    return f"Мониторинг Dexscreener"