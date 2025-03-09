
import logging
from celery.contrib.abortable import AbortableTask
from core.celery import app
from asgiref.sync import async_to_sync
from .monitor import (
    run_dexscreener_monitor_boosted_token, 
    run_dexscreener_monitor_filter_tokens,
    run_dexscreener_parse_top_traders, 
)

logger = logging.getLogger(__name__)


@app.task(bind=True, base=AbortableTask)
def monitor_dexscreener_task(self, settings_ids: list, filter: str, source: str) -> str:
    """
    Обёртывает функцией синхронизации асинхронную функцию мониторинга DexScreener.
    """
    
    async_to_sync(run_dexscreener_monitor_filter_tokens)(
        settings_ids=settings_ids, 
        filter=filter,
        source=source
    )
    
    return f"Мониторинг Dexscreener завершён"


@app.task(bind=True, base=AbortableTask)
def monitor_boosted_tokens_task(self, settings_ids: list, source: str) -> str:
    """
    Обёртывает функцией синхронизации асинхронную функцию мониторинга boosts  
    токенов на DexScreener.
    """
    
    async_to_sync(run_dexscreener_monitor_boosted_token)(
        settings_ids=settings_ids, 
        source=source
    )

    return "Мониторинг boosted токенов на Dexscreener закончен"


@app.task(bind=True, base=AbortableTask)
def parse_dexscreener_task(self, filter: str) -> str:
    """
    Обёртывает функцией синхронизации асинхронную функцию парсинга топов 
    кошельков DexScreener.
    """
    
    async_to_sync(run_dexscreener_parse_top_traders)(filter)

    return "Парсинг топ кошельков на Dexscreener закончен"
