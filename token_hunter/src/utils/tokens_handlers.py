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
    """Performs comprehensive token validation including:
    - Risk analysis via Rugcheck.
    - Data collection from DexTools/DexScreener.
    - Parameter validation against settings.
    - Purchase task initiation for valid tokens.
    
    Executes token purchase if validation passes.

    Args:
        source: Data source ("dextools" or "dexscreener").
        pair: Token pair address.
        token_address: Token contract address.
        telegram_client: Configured Telegram client instance.
        social_data: Dictionary containing token social media data.
        monitoring_rule: Token monitoring rule.
        check_settings_dict: Dictionary with setting IDs and their validation functions.
        boosts_ages: Boost timestamps. Defaults to None.

    Returns:
        True if token passed all validations and tasks were initiated, False otherwise.

    Raises:
        Exception: May propagate exceptions from dependencies (Rugcheck, DexTools etc.).
    
    Notes:
        - High-risk tokens are added to Redis blacklist.
        - In real trading mode (IS_REAL_BUY) initiates actual purchase.
        - Uses synchronous parsing for DEXTools, asynchronous for DEX Screener.
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
    """Returns token validation results from rugcheck.xyz.
    
    Selects data collection method based on configuration.
    
    Args:
        token_address: Token contract address.
        source: Data source ("dextools" or "dexscreener").
        browser: Browser instance for nodriver (optional).
        dex: DexScreenerData or DexToolsData instance based on data source.

    Returns:
        Dictionary containing token validation results.
    """
    if settings.IS_RUGCHECK_API:
        rugcheck_result = rugchek_token_with_api(token_address)
    else:
        if source == "dexscreener":
            rugcheck_result = await scrape_rugcheck_with_nodriver(browser, token_address)
        else:
            rugcheck_result = scrape_rugcheck_with_selenium(dex.driver, token_address)

    return rugcheck_result
