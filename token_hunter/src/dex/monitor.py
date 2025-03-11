import asyncio
import time
import logging
import nodriver as uc
from asgiref.sync import sync_to_async
from django.conf import settings
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from nodriver.core.config import Config
from telethon import TelegramClient
from .transactions_data import DexscreenerData, DextoolsData
from ..token.buyer import real_buy_token
from ..token.checker import TokenChecker, CheckSettings
from ..token.social import get_social_info
from ..token.tasks import buy_token_task, save_top_traders_data_task
from ..token.transfers import get_total_transfers
from ..token.rugcheck import rugcheck, sync_rugcheck
from ..utils.tokens_data import (
    get_pairs_data,
    get_pairs_count, 
    get_latest_boosted_tokens, 
    get_token_data,
    get_token_age
)
from ...models import TopTrader, Transaction, Settings, Mode

try:
    from ...settings import check_api_data, check_settings
except:
    from ...settings_example import check_api_data, check_settings

logger = logging.getLogger(__name__)


class DexScreener():
    def __init__(self, browser=None, check_settings=None, source=None):
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
        """
        Мониторит DexScreener на появление новых токенов Solana.
        Если токен прошёл проверку, то покупает его.
        """
        
        #await self._get_2captcha_api_key()
        if not filter:
            filter = "?rankBy=trendingScoreH6&order=desc&minLiq=1000&minAge=5&maxAge=60"
        
        dex_page = await self.browser.get(
            "https://dexscreener.com/solana/raydium" + filter
        )
        #await self._check_cloudflare(dex_page)
        #await dex_page.wait(10)
        await asyncio.sleep(10)
        
        black_list_links, black_list_pairs = [], []
        step = 0
    
        while True:
            # Регулярное обновление страницы для избежания ошибки "Aw, Snap!" 
            step += 1
            if step == 120:
                await dex_page.reload()
                await asyncio.sleep(5)
                step = 0
                   
            all_links = await dex_page.query_selector_all("a.ds-dex-table-row")

            links = [item for item in all_links if item not in black_list_links]
            await asyncio.sleep(5)
            
            if links:
                for link in links:
                    pair = link.attributes[-1].split("/")[-1]
                    
                    if pair in black_list_pairs:
                        continue

                    token_data = get_pairs_data(pair)[0]
                    
                    if not check_api_data(token_data):
                        continue
                    
                    token_address = token_data["baseToken"]["address"]
                    
                    pair_count = get_pairs_count(token_address)
                    if pair_count != 1:
                        black_list_links.append(link)
                        continue
    
                    await dex_page.wait(2)

                    rugcheck_result = await rugcheck(self.browser, token_address)
                    risk_level = rugcheck_result.get("risk_level")
                    is_mutable_metadata = rugcheck_result.get("is_mutable_metadata")
                    logger.info(f"Уровень риска токена {token_address}: {risk_level}")
                    
                    if risk_level == None:
                        continue
                    elif risk_level != "Good":
                        black_list_links.append(link)
                        continue
  
                    await dex_page.wait(2)

                    # total_transfers = await get_total_transfers(
                    #     browser=self.browser, 
                    #     token_address=token_data["tokenAddress"]
                    # )
                    twitter_data, telegram_data = await get_social_info(
                        browser=self.browser, 
                        social_data=token_data.get("links"), 
                        telegram_client=self.telegram_client
                    )
                    
                    dexscreener = DexscreenerData(self.browser, pair)
                    transaction_data = await dexscreener.get_transactions_data()
                    top_traders_data = transaction_data.get("top_traders_data")
                    snipers_data = transaction_data.get("snipers_data")
                    holders_data = transaction_data.get("holders_data")
                    dextscore = transaction_data.get("dextscore")
                    
                    mode = Mode.DATA_COLLECTION
                    
                    token_checker = TokenChecker(pair, self.check_settings)
                
                    settings_id = token_checker.check_token(snipers_data, top_traders_data)
                    
                    if settings_id:
                        mode = Settings.objects.get(id=settings_id).mode
                        
                    if not check_settings(pair, top_traders_data, snipers_data, holders_data):
                        continue
                        
                    time.sleep(15)
                    upd_token_data =  get_pairs_data(pair)[0]
                    price_15s = float(upd_token_data["priceUsd"])
                    price_change = (price_15s - float(token_data["priceUsd"])) / float(token_data["priceUsd"]) * 100
                            
                    buy_token_task.delay(
                        pair=pair,
                        mode=mode,
                        snipers_data=snipers_data,
                        top_traders_data=top_traders_data,
                        holders_data=holders_data,
                        twitter_data=twitter_data,
                        telegram_data=telegram_data,
                        price_change=price_change,
                        settings_id=settings_id,
                        is_mutable_metadata=is_mutable_metadata,
                        dextscore=dextscore,
                    )
                    
                    black_list_links.append(link)
                    black_list_pairs.append(pair)
                    
            await self.browser.wait(10)
            
    async def monitor_boosted_tokens(self) -> None:
        """
        Мониторит DexScreener на появление новых boodted токенов Solana.
        Если токен прошёл проверку, то покупает его.
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
                
                # if token["amount"] < 500:
                #     continue
                
                if boosted_tokens.get(token["tokenAddress"], {}).get("total_amount") == token["totalAmount"]:
                    continue
                
                token_data = get_token_data(token_address)[0]
                if not token_data.get("liquidity"):
                    black_list.append(token_address)
                    continue
                
                # if not check_api_data(token_data):
                #     continue
                  
                pair = token_data.get("pairAddress")
                
                if self.source == "dextools":
                    dextools = DextoolsData(pair, token["tokenAddress"])
                    rugcheck_result = {}
                    rugcheck_result = sync_rugcheck(dextools.driver, token["tokenAddress"])
                    risk_level = rugcheck_result.get("risk_level")
                    
                    # if risk_level == None:
                    #     continue
                    # if risk_level != "Good":
                    #     black_list.append(token_address)
                    #     continue
                    
                    dextools.open_page()
                    
                    dextscore = dextools.get_dextscore()
                    top_traders_data = dextools.get_top_traders()
                    holders_data = dextools.get_holders()
                    trade_history_data = dextools.get_trade_history()
                    snipers_data = None

                    dextools.close_page()
                    
                else:
                    rugcheck_result = await rugcheck(self.browser, token["tokenAddress"])
                    risk_level = rugcheck_result.get("risk_level")

                    if risk_level == None:
                        continue
                    if risk_level != "Good":
                        black_list.append(token_address)
                        continue

                    twitter_data, telegram_data = await get_social_info(
                        browser=self.browser, 
                        social_data=token.get("links"), 
                        telegram_client=self.telegram_client
                    )
                    
                    dexscreener = DexscreenerData(self.browser, pair)
                    transaction_data = await dexscreener.get_transactions_data()
                    top_traders_data = transaction_data.get("top_traders_data")
                    snipers_data = transaction_data.get("snipers_data")
                    holders_data = transaction_data.get("holders_data")
                    dextscore = None
                    trade_history_data = None

                twitter_data, telegram_data = await get_social_info(
                    browser=self.browser, 
                    social_data=token.get("links"), 
                    telegram_client=self.telegram_client
                )

                mode = Mode.BOOSTED
                
                token_checker = TokenChecker(pair, self.check_settings)
                
                settings_id = token_checker.check_token(top_traders_data=top_traders_data)
                
                if settings_id:
                    mode = Settings.objects.get(id=settings_id).mode
                    
                if not check_settings(pair, top_traders_data, holders_data):
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
                
                buy_token_task.delay(
                    pair=pair,
                    mode=mode,
                    top_traders_data=top_traders_data,
                    snipers_data=snipers_data,
                    holders_data=holders_data,
                    twitter_data=twitter_data,
                    telegram_data=telegram_data,
                    settings_id=settings_id,
                    is_mutable_metadata=rugcheck_result.get("is_mutable_metadata"),
                    dextscore=dextscore,
                    trade_history_data=trade_history_data,
                    boosts_ages=boosted_tokens[token["tokenAddress"]]["boosts_ages"]
                )
                
    async def parse_top_traders(self, filter: str="", pages: int=2) -> None:
        """
        Парсит pages страниц топов кошельков по токенам, ограниченным filter.
        """
        stop_lst_links = []
        
        for page in range(1, pages + 1):
            logger.info(f"Начат парсинг топ кошельков на странице {page}")
            #await self._get_2captcha_api_key()
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
                        logger.debug(f"Токен на странице уже проанализирован")
                        await self.browser.wait(5)
                        continue
                    
                    token_data = get_pairs_data(pair)[0]
                    token_address = token_data["baseToken"]["address"]

                    rugcheck_result = await rugcheck(self.browser, token_address)
                    risk_level = rugcheck_result.get("risk_level")
                    logger.info(f"Уровень риска токена {token_address}: {risk_level}")

                    if risk_level == None:
                        continue
                    if risk_level != "Good":
                        stop_lst_links.append(token_address)
                        continue
                    
                    descreener = DexscreenerData(self.browser, pair)
                    transaction_data = await descreener.get_transactions_data(is_parser=True)
                    top_traders_data = transaction_data.get("top_traders_data")
                    
                    save_top_traders_data_task.delay(
                        pair=pair,
                        token_name=token_data["baseToken"]["name"],
                        token_address=token_address,
                        top_traders_data=top_traders_data
                    )
                    
                    stop_lst_links.append(links)

    @sync_to_async
    def _check_visited_top_traders_link(self, pair: str):
        """
        Проверяет наличие сохранённых топ кошельков токена pair.
        """
        
        return list(TopTrader.objects.all().filter(pair=pair))
    
    @sync_to_async
    def _check_transaction(self, token_address: str):
        """
        Проверяет наличие позиции по покупке токена token_address.
        """
        
        return list(Transaction.objects.filter(token_address=token_address))


async def run_dexscreener_monitor_filter_tokens(settings_ids, filter):
    """
    Инициализирует браузер и запускает мониторинг DesScreener.
    """
    
    config = Config()
    #config.add_extension("./extensions/captcha_solver")
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()
    
    browser = await uc.start(config=config)
    dexscreener = DexScreener(browser, check_settings)
    await dexscreener.monitor_filter_tokens(filter)
    

async def run_dexscreener_monitor_boosted_token(settings_ids: list[int], source: str) -> None:  
    """
    Инициализирует браузер и запускает мониторинг boosted токенов на DesScreener.
    """  
    
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    if source == "dexscreener":
        config = Config(headless=False)
        # config.add_extension("./extensions/captcha_solver")
        browser = await uc.start(config=config, sandbox=False)   
    else:
        browser = None
        
    boosted_worker = DexScreener(browser, check_settings, source)
    await boosted_worker.monitor_boosted_tokens()


async def run_dexscreener_parse_top_traders(filter):  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    dex_worker = DexScreener(browser)
    await dex_worker.parse_top_traders(filter)
    