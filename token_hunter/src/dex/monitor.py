import asyncio
import time
import logging
from asgiref.sync import sync_to_async
from django.conf import settings
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from nodriver.core.browser import Browser
from telethon import TelegramClient
from token_hunter.models import TopTrader, Transaction, Settings, Mode, MonitoringRule
from token_hunter.src.dex.dex_data import DexScreenerData, DexToolsData
from token_hunter.src.token.buyer import real_buy_token
from token_hunter.src.token.checker import TokenChecker
from token_hunter.src.token.social_data import get_social_info
from token_hunter.src.token.tasks import buy_token_task, save_top_traders_data_task
from token_hunter.src.rugcheck.rugcheck_api import rugchek_token_with_api
from token_hunter.src.rugcheck.rugcheck_scraper import (
    scrape_rugcheck_with_nodriver,
    scrape_rugcheck_with_selenium
)
from token_hunter.src.utils.tokens_data import (
    get_pairs_data,
    get_latest_tokens,
    get_latest_boosted_tokens,
    get_token_data,
    get_token_age
)

try:
    from token_hunter.settings import check_api_data, check_settings
except Exception:
    from token_hunter.settings_example import check_api_data, check_settings

logger = logging.getLogger(__name__)


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
        check_settings: list[int]=None, 
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

        app, is_created = App.objects.update_or_create(
        api_id=settings.TELETHON_API_ID,
        api_hash=settings.TELETHON_API_HASH
        )
        cs, cs_is_created = ClientSession.objects.update_or_create(
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

        black_list_links, black_list_pairs = [], []
        step = 0

        while True:
            step += 1
            if step == 120:
                await dex_page.reload()
                await asyncio.sleep(5)
                step = 0
                
            all_links = await dex_page.query_selector_all("a.ds-dex-table-row")
            links = [item for item in all_links if item not in black_list_links]
            await self.browser.wait(10)

            if links:
                for link in links:
                    pair = link.attributes[-1].split("/")[-1]

                    if pair in black_list_pairs:
                        continue

                    token_data = get_pairs_data(pair)[0]

                    if not check_api_data(token_data):
                        continue

                    token_info = await self.get_token_info(
                        pair=pair,
                        token_address=token_data["baseToken"]["address"],
                        token_links=token_data.get("links")
                    )

                    if token_info == 0:
                        black_list_pairs.append(pair)
                        continue
                    if token_info == -1:
                        continue

                    mode = Mode.DATA_COLLECTION
                    token_checker = TokenChecker(pair, self.check_settings)
                    settings_id = token_checker.check_token(
                        top_traders_data=token_info.get("top_traders_data")
                    )

                    if settings_id:
                        mode = Settings.objects.get(id=settings_id).mode

                    if not check_settings(
                        pair, 
                        token_info.get("top_traders_data"), 
                        token_info.get("holders_data")
                    ):
                        continue

                    if settings.IS_REAL_BUY:
                        await real_buy_token(token_data["baseToken"]["address"], self.telegram_client)

                    buy_token_task.delay(
                        pair=pair,
                        mode=mode,
                        monitoring_rule=MonitoringRule.FILTER,
                        top_traders_data=token_info.get("top_traders_data"),
                        snipers_data=token_info.get("snipers_data"),
                        holders_data=token_info.get("holders_data"),
                        twitter_data=token_info.get("twitter_data"),
                        telegram_data=token_info.get("telegram_data"),
                        settings_id=settings_id,
                        is_mutable_metadata=token_info.get("is_mutable_metadata"),
                        dextscore=token_info.get("dextscore"),
                        trade_history_data=token_info.get("trade_history_data"),
                    )

                    black_list_links.append(link)
                    black_list_pairs.append(pair)

            await self.browser.wait(10)

    async def monitor_latest_tokens(self) -> None:
        """Мониторит последние добавленные токены на DexScreener. 
        Инициирует покупку, если они соответствуют критериям в настройках.
        
        Notes:
            Для получения списка недавних токенов использует DEX Screener API.
        """
        if self.source == "dexscreener":
            await self.browser.get("https://dexscreener.com/solana/raydium")

        black_list = []

        while True:
            time.sleep(2)
            boosted_tokens_data = get_latest_tokens()
            for token in boosted_tokens_data:
                if token["chainId"] != "solana":
                    continue

                token_address = token["url"].split("/")[-1]

                if token_address in black_list:
                    continue

                token_data = get_token_data(token_address)[0]
                if not token_data.get("liquidity"):
                    black_list.append(token_address)
                    continue

                if not check_api_data(token_data):
                    continue

                pair = token_data.get("pairAddress")

                token_info = await self.get_token_info(
                    pair=pair,
                    token_address=token["tokenAddress"],
                    token_links=token.get("links")
                )

                if token_info == 0:
                    black_list.append(token_address)
                    continue
                if token_info == -1:
                    continue

                mode = Mode.DATA_COLLECTION
                token_checker = TokenChecker(pair, self.check_settings)
                settings_id = token_checker.check_token(top_traders_data=token_info.get("top_traders_data"))

                if settings_id:
                    mode = Settings.objects.get(id=settings_id).mode

                if not check_settings(pair, token_info.get("top_traders_data"), token_info.get("holders_data")):
                    continue

                if settings.IS_REAL_BUY:
                    await real_buy_token(token["tokenAddress"], self.telegram_client)

                buy_token_task.delay(
                    pair=pair,
                    mode=mode,
                    monitoring_rule=MonitoringRule.LATEST,
                    top_traders_data=token_info.get("top_traders_data"),
                    snipers_data=token_info.get("snipers_data"),
                    holders_data=token_info.get("holders_data"),
                    twitter_data=token_info.get("twitter_data"),
                    telegram_data=token_info.get("telegram_data"),
                    settings_id=settings_id,
                    is_mutable_metadata=token_info.get("is_mutable_metadata"),
                    dextscore=token_info.get("dextscore"),
                    trade_history_data=token_info.get("trade_history_data"),
                )

                black_list.append(token_address)

    async def monitor_boosted_tokens(self) -> None:
        """Мониторит забустенные токены на DexScreener. 
        Инициирует покупку, если они соответствуют критериям в настройках.
        
        Notes:
            Для получения списка забустенных токенов использует DEX Screener API.
        """
        if self.source == "dexscreener":
            await self.browser.get("https://dexscreener.com/solana/raydium")

        black_list, boosted_tokens = [], {}

        while True:
            time.sleep(2)
            boosted_tokens_data = get_latest_boosted_tokens()
            for token in boosted_tokens_data:
                if token["chainId"] != "solana":
                    continue

                token_address = token["url"].split("/")[-1]

                if token_address in black_list:
                    continue

                if token["amount"] < 100:
                    continue

                if boosted_tokens.get(token["tokenAddress"], {}).get("total_amount") == token["totalAmount"]:
                    continue

                token_data = get_token_data(token_address)[0]
                if not token_data.get("liquidity"):
                    black_list.append(token_address)
                    continue

                if not check_api_data(token_data):
                    continue

                pair = token_data.get("pairAddress")

                token_info = await self.get_token_info(
                    pair=pair,
                    token_address=token["tokenAddress"],
                    token_links=token.get("links")
                )

                if token_info == 0:
                    black_list.append(token_address)
                    continue
                if token_info == -1:
                    continue

                mode = Mode.DATA_COLLECTION
                token_checker = TokenChecker(pair, self.check_settings)
                settings_id = token_checker.check_token(top_traders_data=token_info.get("top_traders_data"))

                if settings_id:
                    mode = Settings.objects.get(id=settings_id).mode

                if not check_settings(pair, token_info.get("top_traders_data"), token_info.get("holders_data")):
                    continue

                boosted_tokens.setdefault(
                    token["tokenAddress"],
                    {
                        "total_amount": token["totalAmount"],
                        "boosts_ages": "",
                    })

                upd_token_data =  get_pairs_data(pair)[0]
                token_age = str(get_token_age(upd_token_data["pairCreatedAt"])) + " "

                boosted_tokens[token["tokenAddress"]]["boosts_ages"] += token_age
                boosted_tokens[token["tokenAddress"]]["total_amount"] = token["totalAmount"]

                if settings.IS_REAL_BUY:
                    await real_buy_token(token["tokenAddress"], self.telegram_client)

                buy_token_task.delay(
                    pair=pair,
                    mode=mode,
                    monitoring_rule=MonitoringRule.BOOSTED,
                    top_traders_data=token_info.get("top_traders_data"),
                    snipers_data=token_info.get("snipers_data"),
                    holders_data=token_info.get("holders_data"),
                    twitter_data=token_info.get("twitter_data"),
                    telegram_data=token_info.get("telegram_data"),
                    settings_id=settings_id,
                    is_mutable_metadata=token_info.get("is_mutable_metadata"),
                    dextscore=token_info.get("dextscore"),
                    trade_history_data=token_info.get("trade_history_data"),
                    boosts_ages=boosted_tokens[token["tokenAddress"]]["boosts_ages"]
                )

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

    async def rugcheck_token(
        self,
        token_address: str,
        dex: DexScreenerData | DexToolsData | None=None
    ) -> str | None:
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
            if self.source == "dexscreener":
                rugcheck_result = await scrape_rugcheck_with_nodriver(self.browser, token_address)
            else:
                rugcheck_result = scrape_rugcheck_with_selenium(dex.driver, token_address)

        return rugcheck_result

    async def get_token_info(self, pair: str, token_address: str, token_links: dict) -> dict | int:
        """Собирает полную информацию о токене и выполняет проверку.
        
        Проверяет уровень риска токена на rugcheck.xyz, получает данные о транзакциях и держателях
        токена и о социальных сетях.

        Args:
            pair: Адрес пары токенов.
            token_address: Адрес токена.
            token_links: Ссылки на соцсети токена.

        Returns:
            Словарь с информацией о токене 
                или 0 если токен не прошел проверку
                или -1 если не удалось получить данные.
        """
        dex = (
            DexToolsData(pair, token_address)
            if self.source == "dextools"
            else DexScreenerData(self.browser, pair)
        )

        rugcheck_result = await self.rugcheck_token(token_address, dex)

        if rugcheck_result.get("risk_level") is None:
            return -1
        if rugcheck_result.get("risk_level") != "Good":
            return 0

        token_info = (
            dex.get_dex_data()
            if self.source == "dextools"
            else await dex.get_dex_data()
        )

        token_info["is_mutable_metadata"] = rugcheck_result.get("is_mutable_metadata")
        top_traders_data = token_info.get("top_traders_data")

        if not top_traders_data:
            return 0

        socials_info = await get_social_info(
            browser=self.browser,
            social_data=token_links,
            telegram_client=self.telegram_client
        )

        token_info["twitter_data"] = socials_info.get("twitter_data")
        token_info["telegram_data"] = socials_info.get("telegram_data")

        return token_info

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
