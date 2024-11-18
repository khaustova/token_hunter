import asyncio
import time
import logging
import nodriver as uc
import pandas as pd
import random
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.conf import settings
from nodriver.core.config import Config
from ..tokens.buyer import TokenBuyer
from ..tokens.checker import TokenChecker
from ...models import TopTrader, Transaction, Mode

logger = logging.getLogger(__name__)


class DexScreener():
    def __init__(self, browser):
        self.browser = browser
    
    async def monitor_tokens(self, filter: str) -> None:
        """
        Мониторит DexScreener на появление новых токенов Solana.
        Если токен прошёл проверку, то покупает его.
        """
        
        #await self._get_2captcha_api_key()
        dex_page = await self.browser.get("https://dexscreener.com/solana/raydium" + filter)
        #await self._check_cloudflare(dex_page)
        #await dex_page.wait(10)
        await asyncio.sleep(10)
        black_list, transactions_list = [], []
        all_links = await dex_page.query_selector_all("a.ds-dex-table-row")
        step = 0
        
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
                    pair = link.attributes[-1].split("/")[-1]
                    token_checker = TokenChecker(pair)

                    if link in transactions_list:
                        continue
                    
                    if not token_checker.check_age():
                        black_list.append(link)
                        continue
    
                    await dex_page.wait(2)
 
                    rugcheck = await self.rugcheck(token_checker.token_address)
                    risk_level = rugcheck["risk_level"]
                    is_mutable_metadata = rugcheck["is_mutable_metadata"]
                    logger.info(f"Уровень риска токена {token_checker.token_name}: {risk_level}")
                    
                    # if risk_level == None:
                    #     continue
                    # elif risk_level != "Good":
                    #     black_list.append(link)
                    #     continue
  
                    await dex_page.wait(2)
                    total_transfers = await self.get_total_transfers(token_checker.token_address)
                    if not token_checker.check_transfers(total_transfers):
                        black_list.append(link)
                        continue
                        
                    page = await self.browser.get("https://dexscreener.com" + link.attributes[-1], new_tab=True)
                    
                    time.sleep(5)

                    try:  
                        snipers_button = await page.find("Snipers")
                        time.sleep(3)
                        await snipers_button.click()  
                        time.sleep(3)                            
                        snipers_data = await self.get_snipers(page)
                    except:
                        await page.close()
                        continue
  
                    try:  
                        top_traders_button = await page.find("Top Traders")
                        time.sleep(3)
                        await top_traders_button.click()
                        time.sleep(3)
                        top_traders_data = await self.get_top_traders(page)
                    except:
                        await page.close()
                        continue

                    await page.close()
                    token_buyer = TokenBuyer(pair, total_transfers, is_mutable_metadata)
                    mode = Mode.DATA_COLLECTION
                    await sync_to_async(token_buyer.buy_token)(
                        mode,
                        snipers_data,
                        top_traders_data
                    )
                     
                    transactions_list.append(link)
                    
            await self.browser.wait(10)
        
    async def parse_top_traders(self, filter: str="", pages: int=1) -> None:
        """
        Парсит pages страниц топов кошельков по токенам, ограниченным filter.
        """
        
        for page in range(1, pages + 1):
            logger.info(f"Начат парсинг топ кошельков на странице {page}")
            #await self._get_2captcha_api_key()
            dex_page = await self.browser.get("https://dexscreener.com/solana/page-" + str(page) + filter)
            
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
                    
    async def _clear_number(self, number_str: str) -> float:
        """
        Преобразует переданную строку в число, удаляя лишние символы и 
        обрабатывая значения с "K" и "M".
        """
        
        number_str = number_str.lstrip("$")
        number_str = number_str.replace(",", "").replace(">", "").replace("<", "").replace("$", "")
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


async def run_dexscreener_parser(filter, pages):  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    dex_worker = DexScreener(browser)
    await dex_worker.parse_top_traders(filter, pages)
