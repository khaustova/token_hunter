
import logging
from celery.contrib.abortable import AbortableTask
from core.celery import app
from asgiref.sync import async_to_sync
from .dex_worker import run_dexscreener_watcher, run_dexscreener_parser


logger = logging.getLogger(__name__)

@app.task(bind=True, base=AbortableTask)
def watching_dexscreener_task(self, filter: str) -> str:
    """
    Обёртывает функцией синхронизации асинхронную функцию мониторинга DexScreener.
    """
    
    async_to_sync(run_dexscreener_watcher)(filter)
    
    return f"Мониторинг Dexscreener завершён"


@app.task(bind=True, base=AbortableTask)
def parsing_dexscreener_task(self, filter: str, pages: int) -> str:
    """
    Обёртывает функцией синхронизации асинхронную функцию парсинга топов 
    кошельков DexScreener.
    """
    
    async_to_sync(run_dexscreener_parser)(filter, pages)

    return "Парсинг топ кошельков на Dexscreener закончен"
