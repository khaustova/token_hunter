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
from ..token.tasks import buy_token_task
from ..token.transfers import get_total_transfers
from ..token.rugcheck import rugcheck, sync_rugcheck
from ..utils.tokens_data import (
    get_pairs_data,
    get_pairs_count, 
    get_latest_boosted_tokens, 
    get_token_data,
)
from ...models import TopTrader, Transaction, Settings, Mode
from ...settings import check_settings

logger = logging.getLogger(__name__)


class DexScreener():
    def __init__(self, browser, check_settings):
        self.browser = browser
        self.check_settings = check_settings
        
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
        dex_page = await self.browser.get(
            "https://dexscreener.com/solana/raydium" + filter
        )
        #await self._check_cloudflare(dex_page)
        #await dex_page.wait(10)
        await asyncio.sleep(10)
        black_list, watch_list = [], []
        all_links = await dex_page.query_selector_all("a.ds-dex-table-row")
        step = 0
        await self.telegram_client.connect()
        
        while True:
            # Регулярное обновление страницы для избежания ошибки "Aw, Snap!" 
            step += 1
            if step == 200:
                step = 0
                await dex_page.reload()
                await asyncio.sleep(5)
                   
            all_links = await dex_page.query_selector_all("a.ds-dex-table-row")

            links = [item for item in all_links if item not in black_list]
            await asyncio.sleep(5)
            if links:
                for link in links:
                    pairs = link.attributes[-1].split("/")[-1]
                    token_checker = TokenChecker(pairs)

                    is_transaction = await self._check_transaction(token_checker.token_address)
                    if is_transaction:
                        black_list.append(link)
                        continue
                    
                    if not token_checker.check_age():
                        black_list.append(link)
                        continue
                    
                    pairs_count = get_pairs_count(token_checker.token_address)
                    if pairs_count != 1:
                        black_list.append(link)
                        continue
    
                    await dex_page.wait(2)

                    rugcheck = await self.rugcheck(token_checker.token_address)
                    risk_level = rugcheck["risk_level"]
                    is_mutable_metadata = rugcheck["is_mutable_metadata"]
                    logger.info(f"Уровень риска токена {token_checker.token_name}: {risk_level}")
                    
                    if risk_level == None:
                        continue
                    elif risk_level != "Good":
                        black_list.append(link)
                        continue
  
                    await dex_page.wait(2)
                    #total_transfers = None
                    
                    total_transfers = await self.get_total_transfers(token_checker.token_address)
                        
                    snipers_data, top_traders_data = await self.get_transactions_data(pairs)

                    twitter_data, telegram_data = None, None
                    if token_checker.token_data.get("info"):
                        social_data = token_checker.token_data.get("info").get("socials")
                        if social_data:
                            twitter_data, telegram_data = await self.get_social_data(
                                social_data,
                            )
                            
                    # token_buyer = TokenBuyer(
                    #     pairs, 
                    #     total_transfers, 
                    #     is_mutable_metadata,
                    # )

                    # await sync_to_async(token_buyer.buy_token)(
                    #     Mode.DATA_COLLECTION,
                    #     snipers_data,
                    #     top_traders_data,
                    #     twitter_data,
                    #     telegram_data,
                    # )
                    
            await self.browser.wait(10)
            
    async def monitor_boosted_tokens(self) -> None:
        """
        Мониторит DexScreener на появление новых boodted токенов Solana.
        Если токен прошёл проверку, то покупает его.
        """
        
        await self.browser.get("https://dexscreener.com/solana/raydium")
        await self.browser.get("https://solscan.io/", new_tab=True)
        
        black_list = []
        step = 0
        while True:
            time.sleep(2)
            
            step += 1
            if step == 120:
                logger.debug(f"Получение новых данных по boosted токенам")
                step = 0
                
            boosted_tokens_data = get_latest_boosted_tokens()
            for token in boosted_tokens_data:
                if token["chainId"] != "solana":
                    continue

                token_address = token["url"].split("/")[-1]
                
                if token_address in black_list:
                    continue
                
                if token["amount"] < 500:
                    continue
                
                token_data = get_token_data(token_address)[0]
                if not token_data.get("liquidity"):
                    black_list.append(token_address)
                    continue
                
                pair = token_data.get("pairAddress")

                rugcheck_result = await rugcheck(self.browser, token["tokenAddress"])
                risk_level = rugcheck_result.get("risk_level")
                is_mutable_metadata = rugcheck_result.get("is_mutable_metadata")
                logger.info(f"Уровень риска токена {token["tokenAddress"]}: {risk_level}")

                if risk_level == None:
                    continue
                if risk_level != "Good":
                    black_list.append(token_address)
                    continue

                # total_transfers = get_total_transfers(token["tokenAddress"])
                # twitter_data, telegram_data = get_social_info(token.get("links"))
                
                descreener = DexscreenerData(self.browser, pair)
                transaction_data = await descreener.get_transactions_data()
                top_traders_data = transaction_data.get("top_traders_data")
                snipers_data = transaction_data.get("snipers_data")
                dextscore = transaction_data.get("dextscore")

                mode = Mode.BOOSTED
                
                token_checker = TokenChecker(pair, self.check_settings)
                
                settings_id = token_checker.check_token(snipers_data, top_traders_data)
                
                if settings_id:
                    mode = Settings.objects.get(id=settings_id).mode
                    
                if check_settings(pair, top_traders_data, snipers_data):
                    mode = Mode.REAL
                    
                time.sleep(20)
                price_30s = float(get_pairs_data(pair)[0]["priceUsd"])
                price_change = (price_30s - float(token_data["priceUsd"])) / float(token_data["priceUsd"]) * 100
                
                buy_token_task.delay(
                    pair=pair,
                    mode=mode,
                    snipers_data=snipers_data,
                    top_traders_data=top_traders_data,
                    twitter_data=None,
                    telegram_data=None,
                    price_change=price_change,
                    settings_id=settings_id,
                    is_mutable_metadata=is_mutable_metadata,
                    dextscore=dextscore,
                )
                black_list.append(token_address)
                
    async def parse_top_traders(self, filter: str="", pages: int=1) -> None:
        """
        Парсит pages страниц топов кошельков по токенам, ограниченным filter.
        """
        
        for page in range(1, pages + 1):
            logger.info(f"Начат парсинг топ кошельков на странице {page}")
            #await self._get_2captcha_api_key()
            dex_page = await self.browser.get(
                "https://dexscreener.com/solana/page-" + str(page) + filter
            )
            
            await asyncio.sleep(10)
            
            links = await dex_page.query_selector_all("a.ds-dex-table-row")
            
            await self.browser.wait(10)
            if links:
                for link in links:
                    pair = link.attributes[-1].split("/")[-1]
                    is_visited = await self._check_visited_top_traders_link(pair)
                    if is_visited:
                        logger.debug(f"Токен на странице уже проанализирован")
                        await self.browser.wait(5)
                        continue
                    
                    try:
                        await link.click()
                        await self.browser.wait(3)
                    except:
                        await self.browser.wait(3)
                        continue
                    
                    top_traders_button = await dex_page.find("Top Traders")
                    await top_traders_button.click()
                                        
                    token_link = await dex_page.query_selector_all("a.custom-isf5h9")
                    token_address = token_link[1].attributes[-1].split("/")[-1]
                    
                    await dex_page.wait(10)
                    
                    risk_level = await self.rugcheck_token(token_address)
                    logger.info(f"Уровень риска токена {token_address}: {risk_level}")    
                    if risk_level != "Good":
                        await dex_page.back()
                        await dex_page
                        continue
                    
                    top_traders_button = await dex_page.find("Top Traders")
                    await top_traders_button.click()
                    
                    await dex_page.wait(3)
                    
                    top_traders_data = await self.get_top_traders(dex_page)
                    
                    await dex_page.back()

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


async def run_dexscreener_monitor_filter_tokens(filter):
    """
    Инициализирует браузер и запускает мониторинг DesScreener.
    """
    
    config = Config()
    #config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config)
    dexscreener = DexScreener(browser)
    await dexscreener.monitor_filter_tokens(filter)
    

async def run_dexscreener_monitor_boosted_token(settings_ids):  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config(headless=False)
   # config.add_extension("./extensions/captcha_solver")
    check_settings = {}
    for settings_id in settings_ids:
        check_settings[settings_id] = CheckSettings(settings_id).get_check_functions()

    browser = await uc.start(config=config, sandbox=False)
    boosted_worker = DexScreener(browser, check_settings)
    await boosted_worker.monitor_boosted_tokens()


async def run_top_traders_parser(filter, pages):  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    dex_worker = DexScreener(browser)
    await dex_worker.parse_top_traders(filter, pages)
    
    
async def run_top_traders_parser(filter, pages):  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    dex_worker = DexScreener(browser)
    await dex_worker.parse_top_traders(filter, pages)
