import asyncio
import time
import logging
from asgiref.sync import sync_to_async
from django.conf import settings
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from nodriver.core.browser import Browser
from telethon import TelegramClient
from token_hunter.models import TopTrader, Transaction, MonitoringRule
from token_hunter.src.dex.dex_data import DexScreenerData, DexToolsData
from token_hunter.src.utils.tokens_handlers import process_token
from token_hunter.src.token.tasks import save_top_traders_data_task
from token_hunter.src.utils.tokens_data import (
    get_pairs_data,
    get_latest_tokens,
    get_latest_boosted_tokens,
    get_token_data,
    get_token_age,
)
from token_hunter.storage import get_redis_set, add_to_redis_set

logger = logging.getLogger(__name__)

try:
    from token_hunter.settings import check_api_data
except Exception:
    logger.info("Не удалось импортировать файл с настройками. Импорт настроек по умолчанию (Не рекомендуется)")
    from token_hunter.settings_example import check_api_data

TIMEOUT = 500 # Максимальное время проверки токена

class DexMonitor():
    """Класс для мониторинга и анализа токенов на платформах DEX Screener и DEXTools.
    
    Attributes:
        browser: Экземпляр браузера Chrome или None, если в качестве источника выбран DEXTools.
        сheck_settings: Настройки для выбора токенов.
        source: Источник данных ("dextools" или "dexscreener").
        telegram_client: Созданный и настроенный Telegram-client.
    """

    def __init__(
        self, 
        browser: Browser | None, 
        check_settings: dict | None=None, 
        source: str='dexscreener'
    ):
        """Инициализирует экземпляр DexMonitor.

        Args:
            browser: Экземпляр браузера Chrome или None, если в качестве источника выбран DEXTools.
            сheck_settings: Настройки для выбора токенов.
            source: Источник данных (`dextools` или `dexscreener`).
        """
        self.browser = browser
        self.check_settings = check_settings
        self.source = source

        app, _ = App.objects.update_or_create(
        api_id=settings.TELETHON_API_ID,
        api_hash=settings.TELETHON_API_HASH
        )
        cs, _ = ClientSession.objects.update_or_create(
            name="default",
        )
        self.telegram_client = TelegramClient(
            DjangoSession(client_session=cs),
            app.api_id, 
            app.api_hash
        )

    async def monitor_filter_tokens(self, filter: str) -> None:
        """Открывает страницу DexScreener по фильтру и мониторит появление токенов, 
        соответствующих фильтру. Инициирует покупку, если они соответствуют критериям в настройках.
        
        Notes:
            Для открытия страницы использует библиотеку nodriver и требует ручное 
            прохождение проверки Cloudflare примерно 1 раз в 1.5 суток, поэтому при 
            инициализации браузера нельзя использовать headless.

        Args:
            filter: Параметры фильтрации токенов. По умолчанию ищет трендовые токены
                    с ликвидностью >1000 и возрастом от 5 до 60 минут.
        """
        dex_page = await self.browser.get(
            "https://dexscreener.com/solana/raydium" + filter
        )
        await asyncio.sleep(10)

        step = 0

        while True:
            step += 1
            if step == 120:
                await dex_page.reload()
                await asyncio.sleep(5)
                step = 0
                
            black_list = get_redis_set("black_list")
                
            all_links = await dex_page.query_selector_all("a.ds-dex-table-row")
            await self.browser.wait(10)

            for link in all_links:
                pair = link.attributes[-1].split("/")[-1]
                
                black_list = get_redis_set("black_list")
                processed_tokens = get_redis_set("processed_tokens")
                if pair in black_list or pair in processed_tokens:
                    continue

                token_data = get_pairs_data(pair)[0]
                
                if not token_data.get("liquidity"):
                    add_to_redis_set("black_list", pair)
                    continue

                if not check_api_data(token_data):
                    continue

                add_to_redis_set("processed_tokens", pair)
                try:
                    async with asyncio.timeout(TIMEOUT):
                        result = await process_token(
                            source=self.source,
                            pair=pair, 
                            token_address=token_data["baseToken"]["address"], 
                            telegram_client=self.telegram_client,
                            social_data=token_data.get("links"),
                            check_settings_dict=self.check_settings,
                            monitoring_rule=MonitoringRule.FILTER,
                        )
                except Exception as e:
                    logger.exception(f"Что-то пошло не так с покупкой токена {pair}: {e}")

            await self.browser.wait(10)

    async def monitor_latest_tokens(self) -> None:
        """Мониторит последние добавленные токены на DexScreener. 
        Инициирует покупку, если они соответствуют критериям в настройках.
        
        Notes:
            Для получения списка недавних токенов использует DEX Screener API.
        """
        if self.source == "dexscreener":
            await self.browser.get("https://dexscreener.com/solana/raydium")

        while True:
            time.sleep(2)
            boosted_tokens_data = get_latest_tokens()
            for token in boosted_tokens_data:
                if token["chainId"] != "solana":
                    continue
                
                black_list = get_redis_set("black_list")
                processed_tokens = get_redis_set("processed_tokens")
                token_address = token["url"].split("/")[-1]
                if token_address in black_list or token_address in processed_tokens:
                    continue

                token_data = get_token_data(token_address)[0]

                if not token_data.get("liquidity"):
                    add_to_redis_set("black_list", token_address)
                    continue

                if not check_api_data(token_data):
                    continue

                pair = token_data.get("pairAddress")

                add_to_redis_set("processed_tokens", token_address)
                try:
                    async with asyncio.timeout(TIMEOUT):
                        result = await process_token(
                            source=self.source,
                            pair=pair, 
                            token_address=token["tokenAddress"], 
                            telegram_client=self.telegram_client,
                            social_data=token.get("links"),
                            check_settings_dict=self.check_settings,
                            monitoring_rule=MonitoringRule.LATEST
                        )
                except Exception as e:
                    logger.exception(f"Что-то пошло не так с покупкой токена {pair}: {e}")


    async def monitor_boosted_tokens(self, boosts_min: int=100, boosts_max: int=500) -> None:
        """Мониторит забустенные токены на DexScreener. 
        Инициирует покупку, если они соответствуют критериям в настройках.
        
        Args:
            boosts_min: Минимальный буст. По умолчанию 100.
            boosts_max: Максимальный буст. По умолчанию 500.

        Notes:
            Для получения списка забустенных токенов использует DEX Screener API.
        """
        if self.source == "dexscreener":
            await self.browser.get("https://dexscreener.com/solana/raydium")

        boosted_tokens = {}

        while True:
            time.sleep(2)
            boosted_tokens_data = get_latest_boosted_tokens()
            for token in boosted_tokens_data:
                if token["chainId"] != "solana":
                    continue
                
                black_list = get_redis_set("black_list")
                processed_tokens = get_redis_set("processed_tokens")
                token_address = token["url"].split("/")[-1]
                if token_address in black_list or token_address in processed_tokens:
                    continue

                if token["amount"] < boosts_min or token["amount"] > boosts_max:
                    continue

                if boosted_tokens.get(token["tokenAddress"], {}).get("total_amount") == token["totalAmount"]:
                    continue

                token_data = get_token_data(token_address)[0]

                if not token_data.get("liquidity"):
                    add_to_redis_set("black_list", token_address)
                    continue
                
                if not check_api_data(token_data):
                    continue

                boosted_tokens.setdefault(
                    token["tokenAddress"],
                    {
                        "total_amount": token["totalAmount"],
                        "boosts_ages": "",
                    })

                pair = token_data.get("pairAddress")
                upd_token_data =  get_pairs_data(pair)[0]
                token_age = str(get_token_age(upd_token_data["pairCreatedAt"])) + " "

                boosted_tokens[token["tokenAddress"]]["boosts_ages"] += token_age
                boosted_tokens[token["tokenAddress"]]["total_amount"] = token["totalAmount"]

                add_to_redis_set("processed_tokens", token_address)
                try:
                    async with asyncio.timeout(TIMEOUT):
                        result = await process_token(
                            source=self.source,
                            pair=pair, 
                            token_address=token["tokenAddress"], 
                            telegram_client=self.telegram_client,
                            social_data=token.get("links"),
                            check_settings_dict=self.check_settings,
                            monitoring_rule=MonitoringRule.BOOSTED,
                            boosts_ages=boosted_tokens[token["tokenAddress"]]["boosts_ages"]
                        )
                except Exception as e:
                    logger.error(f"Что-то пошло не так с покупкой токена {pair}: {e}")

    async def parse_top_traders(self, filter: str="", pages: int=1) -> None:
        """Парсит данные о топовых кошельках на DEX Screener или DEXTools.

        Args:
            filter: Фильтр для отбора токенов. По умолчанию пустая строка.
            pages: Количество страниц для парсинга. По умолчанию 1.
        """
        stop_lst_links = []

        for page in range(1, pages + 1):
            logger.info("Начат парсинг топ кошельков на странице %s", page)

            dex_page = await self.browser.get(
                "https://dexscreener.com/solana/page-" + str(page) + filter
            )

            await asyncio.sleep(10)

            all_links = await dex_page.query_selector_all("a.ds-dex-table-row")
            links = [item for item in all_links if item not in stop_lst_links]
            await self.browser.wait(10)

            if links:
                for link in links:
                    pair = link.attributes[-1].split("/")[-1]

                    is_visited = await self._check_visited_top_traders_link(pair)
                    if is_visited:
                        logger.debug("Токен на странице уже проанализирован")
                        await self.browser.wait(5)
                        continue

                    token_data = get_pairs_data(pair)[0]

                    if not check_api_data(token_data):
                        continue

                    dex = (
                        DexToolsData(pair, token_data["baseToken"]["address"])
                        if self.source == "dextools"
                        else DexScreenerData(self.browser, pair)
                    )

                    rugcheck_result = await self.rugcheck_token(token_data["baseToken"]["address"], dex)

                    if rugcheck_result.get("risk_level") is None:
                        return -1
                    if rugcheck_result.get("risk_level") != "Good":
                        return 0

                    top_traders_data = (
                        dex.get_dex_data(is_parser=True)
                        if self.source == "dextools"
                        else await dex.get_dex_data(is_parser=True)
                    )

                    if not top_traders_data:
                        continue

                    save_top_traders_data_task.delay(
                        pair=pair,
                        token_name=token_data["baseToken"]["name"],
                        token_address=token_data["baseToken"]["address"],
                        top_traders_data=top_traders_data
                    )

                    stop_lst_links.append(links)

    @sync_to_async
    def _check_visited_top_traders_link(self, pair: str) -> list[TopTrader]:
        """Проверяет, анализировались ли ранее топовые кошельки для указанной пары.

        Args:
            pair: Адрес пары токенов.

        Returns:
            Список объектов TopTrader для данной пары.
        """
        return list(TopTrader.objects.all().filter(pair=pair))

    @sync_to_async
    def _check_transaction(self, token_address: str) -> list[Transaction]:
        """Проверяет наличие транзакций для указанного токена.

        Args:
            token_address: Адрес токена.

        Returns:
            Список транзакций для данного токена.
        """
        return list(Transaction.objects.filter(token_address=token_address))
