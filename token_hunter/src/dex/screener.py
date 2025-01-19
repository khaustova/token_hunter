import asyncio
import time
import logging
import nodriver as uc
import random
import requests
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from datetime import datetime
from django.conf import settings
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from nodriver.core.config import Config
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from ..tokens.buyer import TokenBuyer
from ..tokens.checker import TokenChecker
from ..utils.tokens_data import (
    get_pairs_data,
    get_pairs_count, 
    get_latest_boosted_tokens, 
    get_token_data
)
from ...models import TopTrader, Transaction, Mode

logger = logging.getLogger(__name__)


class DexScreener():
    def __init__(self, browser):
        self.browser = browser
        
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
    
    async def monitor_tokens(self, filter: str) -> None:
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
                    # if not token_checker.check_transfers(total_transfers):
                    #     black_list.append(link)
                    #     continue
                        
                    snipers_data, top_traders_data = await self.get_transactions_info(pairs)

                    twitter_data, telegram_data = None, None
                    if token_checker.token_data.get("info"):
                        socials_data = token_checker.token_data.get("info").get("socials")
                        if socials_data:
                            twitter_data, telegram_data = await self.get_social_data(
                                socials_data,
                            )
                            
                    token_buyer = TokenBuyer(
                        pairs, 
                        total_transfers, 
                        is_mutable_metadata,
                    )

                    await sync_to_async(token_buyer.buy_token)(
                        Mode.DATA_COLLECTION,
                        snipers_data,
                        top_traders_data,
                        twitter_data,
                        telegram_data,
                    )
                    
            await self.browser.wait(10)
            
    async def monitoring_boosted_tokens(self) -> None:
        """
        Мониторит DexScreener на появление новых boodted токенов Solana.
        Если токен прошёл проверку, то покупает его.
        """
        
        await self.browser.get("https://dexscreener.com/solana/raydium")
        await self.browser.get("https://solscan.io/", new_tab=True)
        
        black_list = []
        BOOSTED_TOKENS = {}
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
                
                if not BOOSTED_TOKENS.get(token_address):
                    rugcheck = await self.rugcheck(token["tokenAddress"])
                    risk_level = rugcheck["risk_level"]
                    is_mutable_metadata = rugcheck["is_mutable_metadata"]
                    logger.info(f"Уровень риска токена {token["tokenAddress"]}: {risk_level}")
  
                    if risk_level == None:
                        continue
                    if risk_level != "Good":
                        black_list.append(token_address)
                        continue

                total_transfers = None
                is_mutable_metadata = False
                snipers_data, top_traders_data = None, None
                twitter_data, telegram_data = None, None
                price_change = None
                #total_transfers = await self.get_total_transfers(token["tokenAddress"])
                    
                snipers_data, top_traders_data = await self.get_transactions_info(token_data.get("pairAddress"))

                #twitter_data, telegram_data = await self.get_social_data(token.get("links"))
                
                token_buyer = TokenBuyer(
                    token_data.get("pairAddress"), 
                    self.telegram_client,
                    total_transfers, 
                    is_mutable_metadata,
                )
                
                mode = Mode.BOOSTED
                
                upd_token_data =  get_pairs_data(token_data.get("pairAddress"))[0]
                
                if snipers_data and top_traders_data:
                    sns_pnl_loss = self.count_pnl_loss(snipers_data["bought"], snipers_data["sold"])
                    tt_pnl_loss = self.count_pnl_loss(top_traders_data["bought"], top_traders_data["sold"])
                
                    if (upd_token_data["txns"]["m5"]["sells"] < 400 
                        and upd_token_data["txns"]["h1"]["sells"] < 1000
                        and upd_token_data["marketCap"] < 500000
                        and upd_token_data["boosts"].get("active") == 500
                        and upd_token_data["priceChange"]["m5"] <= 60
                        and upd_token_data["priceChange"]["m5"] >= -60
                        and sns_pnl_loss <= 20
                        and tt_pnl_loss <= 20   
                    ):
                        mode = Mode.REAL
                    
                # time.sleep(30)
                # price_30s = float(get_pairs_data(token_data.get("pairAddress"))[0]["priceUsd"])
                # price_change = (price_30s - float(token_data["priceUsd"])) / float(token_data["priceUsd"]) * 100
                
                
                await sync_to_async(token_buyer.buy_token)(
                    mode,
                    snipers_data,
                    top_traders_data,
                    twitter_data,
                    telegram_data,
                    price_change,
                )
                black_list.append(token_address)
                    
                    
            
    async def get_transactions_info(self, pairs: str) -> tuple:
        """
        Открывает страницу токена и сохраняет информацию о транзакциях
        снайперов и топ трейдеров.
        """

        page = await self.browser.get(
            "https://dexscreener.com/solana/" + pairs, 
            new_tab=True
        )

        time.sleep(5)
        await page.wait(10)
        try:  
            snipers_button = await page.find("Snipers")
            await snipers_button.click()  
            time.sleep(3)                            
            snipers_data = await self.get_snipers(page)
        except:
            snipers_data = None

        time.sleep(5)
        try:  
            top_traders_button = await page.find("Top Traders")
            await top_traders_button.click()
            time.sleep(3)
            top_traders_data = await self.get_top_traders(page)
        except:
            top_traders_data = None

        await page.close()
        
        return (snipers_data, top_traders_data)
    
    async def count_pnl_loss(self, bought_str: str, sold_str: str) -> int:
        """
        Возвращает количество отрицательных PNL.
        """
        try:
            bought_lst = [float(x) for x in bought_str.split(" ")]
            sold_lst = [float(x) for x in sold_str.split(" ")]
            pnl_lst = [sold - bought if sold else 0 for bought, sold in zip(bought_lst, sold_lst)]
            
            pnl_loss = sum(i < 0 for i in pnl_lst)
            
            return pnl_loss
        except:
            return 100
    
    async def get_social_data(self, socials_data: dict) -> tuple:
        """
        Возвращает данные о телеграме и твиттере токена.
        """
        
        twitter_data, telegram_data = None, None
        if socials_data:
            for data in socials_data:
                if data.get("type") == "twitter":
                    twitter_name = data.get("url").split("/")[-1]
                    twitter_data = await self.get_twitter_data(twitter_name)
                elif data.get("type") == "telegram":
                    channel_name = data.get("url").split("/")[-1]
                    telegram_data = await self.get_telegram_data(channel_name)
                        
        return (twitter_data, telegram_data)

        
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
                    
                    
    async def get_snipers(self, page) -> dict:
        """
        Получает данные о покупках и продажах из таблицы Snipers на странице 
        токена. Подсчитывает количество значений в зависимости от диапазона, 
        а также количество снайперов, держащих или продавших (часть или всё).
        Сохраняет информацию о первых десяти транзакциях.
        Возвращает результат в виде словаря.
        """
        
        snipers_table = await page.query_selector(
            "main > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
        )
        await snipers_table
        snipers_table_html = await snipers_table.get_html()    
        
        soup = BeautifulSoup(snipers_table_html, "html.parser")
        snipers_data = {
            "held_all": 0,
            "sold_all": 0,
            "sold_some": 0,
        }
        
        main_div = soup.find("div", recursive=False)
        snipers_divs = main_div.find_all("div", recursive=False)
        bought_lst, sold_lst = [], []
        
        for divs in snipers_divs[1:]:
            snipers_spans = divs.find_all("span")
            bought = await self._get_list_element_by_index(snipers_spans, 5)
            sold = "-"
            pnl = 0
            
            operation = await self._get_list_element_by_index(snipers_spans, 2)
            if operation == "Held all":
                snipers_data["held_all"] += 1
                if bought != "-":
                    bought = await self._clear_number(bought)
                    
            elif operation == "Sold all" or operation == "Sold some":
                if operation == "Sold all":
                    snipers_data["sold_all"] += 1
                elif operation == "Sold some":
                    snipers_data["sold_some"] += 1
                    
                if bought != "-":
                    bought = await self._clear_number(bought)
                    sold = await self._get_list_element_by_index(snipers_spans, 10)
                        
                    if sold != "-":
                        sold = await self._clear_number(sold)
                        pnl = sold - bought
                else:
                    sold = await self._get_list_element_by_index(snipers_spans, 6)
                    if sold != "-":
                        sold = await self._clear_number(sold)
                        pnl = sold
  
            if bought != "-":
                bought_lst.append(bought)
            else:
                bought_lst.append(0)
                
            if sold != "-":
                sold_lst.append(sold)
            else:
                sold_lst.append(0)
                
        
        snipers_data["bought"] = " ".join(map(str, bought_lst))
        snipers_data["sold"] = " ".join(map(str, sold_lst))
 
        return snipers_data
                    
    async def get_top_traders(self, page, mode="monitor") -> dict:
        """
        Получает данные о покупках и продажах из таблицы Top Traders на странице 
        токена. Подсчитывает количество значений в зависимости от диапазона
        и возвращает результат в виде словаря.
        """
        
        await page.wait(2)
        top_traders_table = await page.query_selector(
            "main > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
        )
        await top_traders_table
        top_traders_table_html = await top_traders_table.get_html()

        soup = BeautifulSoup(top_traders_table_html, "html.parser")
        top_traders_data = {}
        
        main_div = soup.find("div", recursive=False)
        top_traders_divs = main_div.find_all("div", recursive=False)
        bought_lst, sold_lst = [], []
        for divs in top_traders_divs[1:]:
            top_trader_spans = divs.find_all("span")
            
            if mode == "parse":
                top_trader_link = divs.find("a")["href"]
                wallet_address = top_trader_link.split("/")[-1]
                
            bought = await self._get_list_element_by_index(top_trader_spans, 2)

            if bought == "-":
                sold = await self._get_list_element_by_index(top_trader_spans, 3)
                if sold != "-":
                    sold = await self._clear_number(sold)
            else:
                bought = await self._clear_number(bought)
                sold = await self._get_list_element_by_index(top_trader_spans, 7)
                if sold != "-":
                    sold = await self._clear_number(sold)
                
            if bought != "-":
                bought_lst.append(bought)
            else:
                bought_lst.append(0)
                
            if sold != "-":
                sold_lst.append(sold)
            else:
                sold_lst.append(0)

        top_traders_data["bought"] = " ".join(map(str, bought_lst))
        top_traders_data["sold"] = " ".join(map(str, sold_lst))
            
        return top_traders_data
    
    async def rugcheck(self, token_address):
        """
        Возвращает уровень риска токена token_address с rugcheck.xyz. 
        """
        
        rugcheck_page = await self.browser.get(
            "https://rugcheck.xyz/tokens/" + token_address, 
            new_tab=True
        )
        await rugcheck_page
        
        time.sleep(5)
       
        risk_level = None 
        try:
            risk_level_element = await rugcheck_page.query_selector("div.risk h1.mb-0")
            risk_level = risk_level_element.text
        except:
            pass
        
        try:
            mutable_metadata = await rugcheck_page.find("Mutable metadata")
            is_mutable_metadata = True
        except:
            is_mutable_metadata = False
            
        result = {
            "risk_level": risk_level,
            "is_mutable_metadata": is_mutable_metadata,
        }
            
        await rugcheck_page.close()
        
        return result
    
    async def get_twitter_data(self, twitter_name: str) -> dict:
        """
        Получает данные о твиттере токена: количестве подписчиков, 
        в т.ч. известных, возрасте аккаунта и количестве твитов,  
        """
        
        getmoni_page = await self.browser.get(
            "https://discover.getmoni.io/" + twitter_name, 
            new_tab=True
        )
        await getmoni_page
        
        time.sleep(8)
        twitter_data = {}
        
        try:
            not_found = await getmoni_page.find("Not found")
        except:
            not_found = False
            
        if not_found:
            twitter_data["is_twitter_error"] = True
            return twitter_data
        
        try:
            page_src = await getmoni_page.query_selector(
                "main > div > div"
            )
            await page_src
            page_html = await page_src.get_html()
            soup = BeautifulSoup(page_html, "html.parser")
            
            followers_element = (
                soup
                .find("div")
                .find_all("section")[1]
                .find_all("article")[0]
                .find("div")
                .find_all("div")[1]
            )
            twitter_data["twitter_followers"] = (
                followers_element
                .find_all("div")[3]
                .find_all("span")[0]
                .text
            )
            twitter_data["twitter_followers"] = await self._clear_number(twitter_data["twitter_followers"])
            twitter_data["twitter_smart_followers"] = (
                followers_element
                .find_all("div")[6]
                .find_all("span")[1]
                .text
            )
            twitter_data["twitter_smart_followers"] = await self._clear_number(twitter_data["twitter_smart_followers"])
            twitter_data["is_twitter_error"] = False
            
            info_element = (
                soup
                .find("div")
                .find_all("div", recursive=False)[0]
                .find_all("article")[1]
            )
            created_date_str = (
                info_element
                .find_all("li")[1]
                .find_all("span")[1]
                .text
            )
            created_date = datetime.strptime(created_date_str, "%d %b %Y").date()
            twitter_data["twitter_days"] = (datetime.now().date() - created_date).days
            twitter_data["twitter_tweets"] = (
                info_element
                .find_all("li")[-1]
                .find_all("span")[1]
                .text
            )
            if twitter_data["twitter_tweets"] == "—":
                twitter_data["twitter_tweets"] = 0
            else:
                try:
                    twitter_data["twitter_tweets"] = await self._clear_number(twitter_data["twitter_tweets"])
                except:
                    twitter_data["twitter_tweets"] = -1
            
        except:
            pass
        
        await getmoni_page.close()

        return twitter_data    

    async def get_telegram_data(self, raw_channel_name: str) -> dict:
        """
        Получает данные о телеграм-канале токена: количестве подписчиков, 
        возрасте первого чата и наличии отметки 'скам'.
        """
        
        channel_name = ""
        for letter in raw_channel_name:
            if letter.isalnum() or letter == "_":
                channel_name += letter;
            else:
                break

        telegram_data = {}
        
        await self.telegram_client.connect()
        
        try:       
            channel_connect = await self.telegram_client.get_entity(channel_name)
            channel_full_info = await self.telegram_client(GetFullChannelRequest(channel=channel_connect))
            telegram_data["telegram_members"] = int(channel_full_info.full_chat.participants_count)
            telegram_data["is_telegram_error"] = False
        except:
            telegram_data["is_telegram_error"] = True
        
        await self.telegram_client.disconnect()
        
        return telegram_data
                    
    async def _clear_number(self, number_str: str) -> float:
        """
        Преобразует переданную строку в число, удаляя лишние символы и 
        обрабатывая значения с "K" и "M".
        """
        
        number_str = number_str.lstrip("$")
        number_str = (
            number_str
            .replace(",", "")
            .replace(">", "")
            .replace("<", "")
            .replace("$", "")
            .replace(" ", "")
        )
        if number_str[-1] == "K":
            number_str = number_str[:-1]
            number = float(number_str) * 1000
        elif number_str[-1] == "M":
            number_str = number_str[:-1]
            number = float(number_str) * 1000000
        else:
            number = float(number_str)
        
        return number

    async def get_total_transfers(self, token_address):
        """
        Возвращает количество трансферов токена token_address с solscan.io.
        """
        
        solcan_page = await self.browser.get(
            "https://solscan.io/token/" + token_address, 
            new_tab=True
        )
        await solcan_page
        
        time.sleep(7)

        total_transfers = None 
        try:
            total_transfers_div = await solcan_page.find("transfer(s)")
            total_transfers_list = total_transfers_div.text_all.split()
            if total_transfers_list[0] == "More":
                total_transfers = total_transfers_list[2].replace(",", "")
            elif total_transfers_list[0] == "Total":
                total_transfers = total_transfers_list[1].replace(",", "")
        except:
            pass
            
        await solcan_page.close()
 
        return int(total_transfers) if total_transfers else None
      
    async def _check_cloudflare(self, page):
        """
        Проверяет наличие защиты Cloudflare.
        """
        
        await self.browser.wait(random.randint(1, 2))
        try:
            await page.find("Verifying you are human")
            await self._bypass_cloudflare(page)
        except:
            return None

    async def _bypass_cloudflare(self, page):
        """
        Проходит Cloudflare с помощью расширения 2captcha.
        """
        
        try:
            captcha_solve_button = await page.find("Solve with 2captcha")
            await captcha_solve_button.click()
        except:
            logger.debug("Кнопка 2Captcha не найдена, повтор попытки")
            await page.reload()
            await self._bypass_cloudflare(page)
            
        while True:
            try:
                await page.find("Verifying you are human.")
                logger.debug("Ожидание ответа от 2captcha...")
                await self.browser.wait(5)
            except:
                break
            
        logger.info("Защита Cloudflare успешно пройдена")
        
    async def _get_2captcha_api_key(self):
        """
        Вводит API ключ для работы расширения 2captcha.
        """
        
        captcha_extenshion_page = await self.browser.get(settings.CAPTCHA_EXTENSION_LINK)
        api_key_input = await captcha_extenshion_page.select("input[name=apiKey]")
        
        await api_key_input.send_keys(settings.CAPTCHA_API_KEY)
        login_button = await captcha_extenshion_page.find("Login")
        await login_button.click()
        
    async def _get_list_element_by_index(self, lst: list, ind: int) -> str:
        """
        Возвращает элемент списка с индексом ind.
        Если его не существует, то возвращает "-".
        """
        
        try:
            result = lst[ind].text
        except IndexError:
            result = "-"
            
        return result
        
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


async def run_dexscreener_watcher(filter):
    """
    Инициализирует браузер и запускает мониторинг DesScreener.
    """
    
    config = Config()
    #config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config)
    dexscreener = DexScreener(browser)
    await dexscreener.monitor_tokens(filter)
    

async def run_dexscreener_boosted_watcher():  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config(headless=False)
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    boosted_worker = DexScreener(browser)
    await boosted_worker.monitoring_boosted_tokens()


async def run_dexscreener_parser(filter, pages):  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    dex_worker = DexScreener(browser)
    await dex_worker.parse_top_traders(filter, pages)
