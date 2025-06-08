import logging
import nodriver as uc
from nodriver.core.config import Config
from asgiref.sync import async_to_sync
from celery.contrib.abortable import AbortableTask
from core.celery import app
from django.db import OperationalError
from token_hunter.src.dex.monitor import DexMonitor
from token_hunter.src.token.checker import CheckSettings

logger = logging.getLogger(__name__)


async def start_monitoring_filtered_tokens(settings_ids: list[int], filter: str, source: str) -> None:
    """Configures browser and initiates filtered token monitoring on DEX Screener.
    
    Args:
        settings_ids: List of settings IDs for token selection criteria.
        filter: Token filtering parameters.
        source: Data source ('dextools' or 'dexscreener').
    """
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    config = Config(headless=False)
    browser = await uc.start(config=config, sandbox=False)

    monitor = DexMonitor(browser=browser, check_settings=check_settings, source=source)
    await monitor.monitor_filter_tokens(filter)


@app.task(
    bind=True, 
    base=AbortableTask,
    autoretry_for=(OperationalError,), 
    retry_backoff=60, 
    max_retries=5
)
def monitor_filtered_tokens_task(self, settings_ids: list[int], filter: str, source: str) -> str:
    """Celery task for filtered token monitoring.
    
    Args:
        self: Celery task instance.
        settings_ids: List of settings IDs for token selection.
        filter: Token filtering parameters.
        source: Data source ('dextools' or 'dexscreener').

    Returns:
        Task completion message.
    """
    async_to_sync(start_monitoring_filtered_tokens)(
        settings_ids=settings_ids,
        filter=filter,
        source=source
    )

    return "Filtered token monitoring completed"


async def start_monitoring_boosted_token(
    settings_ids: list[int], 
    source: str,
    boosts_min: int,
    boosts_max: int) -> None:
    """Initiates monitoring of boosted tokens using DEX Screener API.
    
    Args:
        settings_ids: List of settings IDs for token selection.
        source: Data source ('dextools' or 'dexscreener').
        boosts_min: Minimum boost count threshold.
        boosts_max: Maximum boost count threshold.
    """
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    if source == "dexscreener":
        config = Config(headless=False)
        browser = await uc.start(config=config, sandbox=False)   
    else:
        browser = None

    monitor = DexMonitor(browser=browser, check_settings=check_settings, source=source)
    await monitor.monitor_boosted_tokens(boosts_min=boosts_min, boosts_max=boosts_max)


@app.task(
    bind=True, 
    base=AbortableTask,
    autoretry_for=(OperationalError,), 
    retry_backoff=60, 
    max_retries=5
)
def monitor_boosted_tokens_task(
    self, 
    settings_ids: list, 
    source: str, 
    boosts_min: int,
    boosts_max: int) -> str:
    """Celery task for boosted token monitoring.
    
    Args:
        self: Celery task instance.
        settings_ids: List of settings IDs for token selection.
        source: Data source ('dextools' or 'dexscreener').
        boosts_min: Minimum boost count threshold.
        boosts_max: Maximum boost count threshold.

    Returns:
        Task completion message.
    """
    async_to_sync(start_monitoring_boosted_token)(
        settings_ids=settings_ids,
        source=source,
        boosts_min=boosts_min,
        boosts_max=boosts_max,
    )

    return "Boosted token monitoring completed"


async def start_monitoring_latest_token(settings_ids: list[int], source: str) -> None:  
    """Initiates monitoring of recently listed tokens using DEX Screener API.
    
    Args:
        settings_ids: List of settings IDs for token selection.
        source: Data source ('dextools' or 'dexscreener').
    """
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    if source == "dexscreener":
        config = Config(headless=False)
        browser = await uc.start(config=config, sandbox=False)   
    else:
        browser = None

    monitor = DexMonitor(browser=browser, check_settings=check_settings, source=source)
    await monitor.monitor_latest_tokens()


@app.task(
    bind=True, 
    base=AbortableTask,
    autoretry_for=(OperationalError,), 
    retry_backoff=60, 
    max_retries=5
)
def monitor_latest_tokens_task(self, settings_ids: list, source: str) -> str:
    """Celery task for recently listed token monitoring.
    
    Args:
        self: Celery task instance.
        settings_ids: List of settings IDs for token selection.
        source: Data source ('dextools' or 'dexscreener').

    Returns:
        Task completion message.
    """
    async_to_sync(start_monitoring_latest_token)(
        settings_ids=settings_ids,
        source=source
    )

    return "Recently listed token monitoring completed"


async def start_parsing_top_traders(filter: str, source: str) -> None:
    """Initiates parsing of top trader wallets from DEX Screener or DEXTools.
    
    Args:
        filter: Token filtering parameters for wallet selection.
        source: Data source ('dextools' or 'dexscreener').
    """
    config = Config(headless=False)
    browser = await uc.start(config=config, sandbox=False)   
    monitor = DexMonitor(browser=browser, source=source)
    await monitor.parse_top_traders(filter)


@app.task(
    bind=True, 
    base=AbortableTask,
    autoretry_for=(OperationalError,), 
    retry_backoff=60, 
    max_retries=5
)
def parse_top_traders_task(self, filter: str, source: str) -> str:
    """Celery task for top trader wallet parsing.
    
    Args:
        self: Celery task instance.
        filter: Token filtering parameters for wallet selection.
        source: Data source ('dextools' or 'dexscreener').

    Returns:
        Task completion message.
    """
    async_to_sync(start_parsing_top_traders)(filter=filter, source=source)

    return "Top trader wallet parsing completed"
