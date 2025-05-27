from django.conf import settings
from nodriver.core.browser import Browser
from telethon import TelegramClient
from token_hunter.models import Mode, MonitoringRule, Settings
from token_hunter.src.dex.dex_data import DexScreenerData, DexToolsData
from token_hunter.src.token.buyer import real_buy_token
from token_hunter.src.token.checker import TokenChecker
from token_hunter.src.rugcheck.rugcheck_api import rugchek_token_with_api
from token_hunter.src.rugcheck.rugcheck_scraper import (
    scrape_rugcheck_with_nodriver,
    scrape_rugcheck_with_selenium
)
from token_hunter.src.token.social_data import get_telegram_data
from token_hunter.src.token.tasks import buy_token_task
from token_hunter.storage import add_to_redis_set

try:
    from token_hunter.settings import check_settings
except Exception:
    from token_hunter.settings_example import check_settings
    

async def process_token(
    source: str,
    pair: str, 
    token_address: str,
    telegram_client: TelegramClient, 
    social_data: dict, 
    monitoring_rule: MonitoringRule,
    check_settings_dict: dict,
    boosts_ages: str | None=None,
) -> bool:
    """Выполняет комплексную проверку токена включая:
    - Анализ рисков через Rugcheck
    - Сбор данных с DexTools/DexScreener
    - Проверку параметров согласно настройкам
    - Запуск задач на покупку при успешных проверках
    
    Если токен прошёл проверку, то выполняет покупку токена.

    Args:
        source: Источник данных ("dextools" или "dexscreener").
        pair: Адрес пары токена.
        token_address: Адрес токена.
        telegram_client: Созданный и настроенный Telegram-client.
        social_data: Словарь с данными по социальным сетям токена.
        monitoring_rule: Правило мониторинга токена.
        check_settings: Словарь с ID настроек и их функциями проверки токена.
        boosts_ages: Временные метки бустов. По умолчанию None.

    Returns:
        True если токен прошел все проверки и задачи запущены, False в противном случае.

    Raises:
        Exception: Может пробрасывать исключения зависимостей (Rugcheck, DexTools и др.).
    
    Notes:
        - При обнаружении высокого риска токен добавляется в черный список в Redis.
        - В режиме реальной торговли (IS_REAL_BUY) инициирует реальную покупку.
        - Для DEXTools используется синхронный парсинг, для DEX Screener - асинхронный.
    """
    dex = (
        DexToolsData(pair, token_address)
        if source == "dextools"
        else DexScreenerData(pair)
    )

    rugcheck_result = await rugcheck_token(token_address, dex)

    if rugcheck_result.get("risk_level") is None:
        return False
    if rugcheck_result.get("risk_level") != "Good":
        add_to_redis_set("black_list", token_address.lower())
        return False

    token_info = (
        dex.get_dex_data()
        if source == "dextools"
        else await dex.get_dex_data()
    )

    if not token_info or not token_info.get("top_traders_data"):
        add_to_redis_set("black_list", token_address.lower())
        return False
    
    token_info["is_mutable_metadata"] = rugcheck_result.get("is_mutable_metadata")
 
    mode = Mode.DATA_COLLECTION

    token_checker = TokenChecker(pair, check_settings_dict)
    settings_id = token_checker.check_token(top_traders_data=token_info.get("top_traders_data"))

    if settings_id:
        mode = Settings.objects.get(id=settings_id).mode

    token_info["telegram_data"] = await get_telegram_data(
        telegram_client=telegram_client,
        social_data=social_data,
    )

    if not check_settings(pair, token_info):
        return False

    if settings.IS_REAL_BUY:
        await real_buy_token(token_address)

    buy_token_task.delay(
        pair=pair,
        mode=mode,
        monitoring_rule=monitoring_rule,
        top_traders_data=token_info.get("top_traders_data"),
        snipers_data=token_info.get("snipers_data"),
        holders_data=token_info.get("holders_data"),
        twitter_data=None,
        telegram_data=token_info.get("telegram_data"),
        settings_id=settings_id,
        is_mutable_metadata=token_info.get("is_mutable_metadata"),
        dextscore=token_info.get("dextscore"),
        trade_history_data=token_info.get("trade_history_data"),
        boosts_ages=boosts_ages
    )
    
    return True


async def rugcheck_token(
    token_address: str,
    source: str,
    browser: Browser | None=None,
    dex: DexScreenerData | DexToolsData | None=None
) -> int | None:
    """Возвращает словарь с результатами проверки токена на rugcheck.xyz.
    
    В зависимости от настроек выбирает способ получения данных на RugCheck.
    
    Args:
        token_address: Адрес токена.
        dex: Экземпляр класса DexScreenerData или DexToolsData  
            в зависимости от выбранного источника данных.

    Returns:
        Словарь с результатами проверки токена.
    """
    if settings.IS_RUGCHECK_API:
        rugcheck_result = rugchek_token_with_api(token_address)
    else:
        if source == "dexscreener":
            rugcheck_result = await scrape_rugcheck_with_nodriver(browser, token_address)
        else:
            rugcheck_result = scrape_rugcheck_with_selenium(dex.driver, token_address)

    return rugcheck_result
