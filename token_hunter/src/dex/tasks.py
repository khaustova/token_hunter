import logging
import nodriver as uc
from nodriver.core.config import Config
from asgiref.sync import async_to_sync
from celery.contrib.abortable import AbortableTask
from core.celery import app
from token_hunter.src.dex.monitor import DexMonitor
from token_hunter.src.token.checker import CheckSettings

logger = logging.getLogger(__name__)


async def start_monitoring_filtered_tokens(settings_ids: list[int], filter: str, source: str) -> None:
    """Создаёт и настраивает браузер для использования библиотеки nodriver и запускает мониторинг 
    токенов на DEX Screener по заданному фильтру.

    Args:
        settings_ids: Список ID настроек для выбора токенов.
        filter: Параметры фильтрации токенов.
        source: Источник данных (`dextools` или `dexscreener`).
    """
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    config = Config(headless=False)
    browser = await uc.start(config=config, sandbox=False)

    monitor = DexMonitor(browser, check_settings, source)
    await monitor.monitor_filter_tokens(filter)


@app.task(bind=True, base=AbortableTask)
def monitor_filtered_tokens_task(self, settings_ids: list[int], filter: str, source: str) -> str:
    """Задача мониторинга токенов по фильтру.

    Args:
        self: Экземпляр задачи Celery.
        settings_ids: Список ID настроек для выбора токенов.
        filter: Параметры фильтрации токенов.
        source: Источник данных (`dextools` или `dexscreener`).

    Returns:
        str: Сообщение о завершении задачи.
    """
    async_to_sync(start_monitoring_filtered_tokens)(
        settings_ids=settings_ids,
        filter=filter,
        source=source
    )

    return "Мониторинг токенов по фильтру завершён"


async def start_monitoring_boosted_token(settings_ids: list[int], source: str) -> None:
    """Запускает мониторинг забустенных на DEX Screener токенов. 
    
    Для получения списка токенов использует DEX Screener API.
    
    Notes:
        Если в качестве источника данных для анализа выбранного токена выбран DEX Screener, 
        то создаёт и настраивает браузер для использования библиотеки nodriver.

    Args:
        settings_ids: Список ID настроек для выбора токенов.
        source: Источник данных (`dextools` или `dexscreener`).
    """
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    if source == "dexscreener":
        config = Config(headless=False)
        browser = await uc.start(config=config, sandbox=False)   
    else:
        browser = None

    monitor = DexMonitor(browser, check_settings, source)
    await monitor.monitor_boosted_tokens()


@app.task(bind=True, base=AbortableTask)
def monitor_boosted_tokens_task(self, settings_ids: list, source: str) -> str:
    """Задача мониторинга забустенных токенов.

    Args:
        self: Экземпляр задачи Celery.
        settings_ids: Список ID настроек для выбора токенов.
        source: Источник данных (`dextools` или `dexscreener`).

    Returns:
        str: Сообщение о завершении задачи.
    """
    async_to_sync(start_monitoring_boosted_token)(
        settings_ids=settings_ids,
        source=source
    )

    return "Мониторинг забустенных токенов закончен"


async def start_monitoring_latest_token(settings_ids: list[int], source: str) -> None:  
    """Запускает мониторинг недавно добавленных на DEX Screener токенов. 
    
    Для получения списка токенов использует DEX Screener API.
    
    Notes:
        Если в качестве источника данных для анализа выбранного токена выбран DEX Screener, 
        то создаёт и настраивает браузер для использования библиотеки nodriver.

    Args:
        settings_ids: Список ID настроек для выбора токенов.
        source: Источник данных (`dextools` или `dexscreener`).
    """
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    if source == "dexscreener":
        config = Config(headless=False)
        browser = await uc.start(config=config, sandbox=False)   
    else:
        browser = None

    monitor = DexMonitor(browser, check_settings, source)
    await monitor.monitor_latest_tokens()


@app.task(bind=True, base=AbortableTask)
def monitor_latest_tokens_task(self, settings_ids: list, source: str) -> str:
    """Задача мониторинга недавно добавленных токенов.

    Args:
        self: Экземпляр задачи Celery.
        settings_ids: Список ID настроек для выбора токенов.
        source: Источник данных (`dextools` или `dexscreener`).

    Returns:
        str: Сообщение о завершении задачи.
    """
    async_to_sync(start_monitoring_latest_token)(
        settings_ids=settings_ids,
        source=source
    )

    return "Мониторинг недавних токенов закончен"


async def start_parsing_top_traders(filter: str, source: str) -> None:
    """Запускает парсинг топовых кошельков на DEX Screener или DEXTools.

    Args:
        filter: Параметры фильтрации токенов, по которым парсятся топовые кошельки.
        source: Источник данных (`dextools` или `dexscreener`).
        
    Notes:
        Если в качестве источника данных для анализа выбран DEX Screener, то создаёт и настраивает 
        браузер для использования библиотеки nodriver.
    """
    config = Config(headless=False)
    browser = await uc.start(config=config, sandbox=False)   
    monitor = DexMonitor(browser=browser, source=source)
    await monitor.parse_top_traders(filter)


@app.task(bind=True, base=AbortableTask)
def parse_top_traders_task(self, filter: str, source: str) -> str:
    """Задача парсинга топовых кошельков на DEX Screener или DEXTools.

    Args:
        self: Экземпляр задачи Celery.
        filter: Параметры фильтрации токенов, по которым парсятся топовые кошельки.
        source: Источник данных (`dextools` или `dexscreener`).

    Returns:
        str: Сообщение о завершении задачи.
    """
    async_to_sync(start_parsing_top_traders)(filter=filter, source=source)

    return "Парсинг топовых кошельков закончен"

