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
        dex_page = await self.browser.get('https://dexscreener.com/solana/raydium' + filter)
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
 
                    risk_level = await self.rugcheck(token_checker.token_address)
                    logger.info(f"Уровень риска токена {token_checker.token_name}: {risk_level}")
                    
                    if risk_level == None:
                        continue
                    elif risk_level != "Good":
                        black_list.append(link)
                        continue
  
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

                    token_buyer = TokenBuyer(pair, total_transfers)
                    
                    if (top_traders_data and 
                        snipers_data and
                        top_traders_data.get("sum_sold") != 0 and 
                        top_traders_data.get("sum_bought") != 0 and
                        top_traders_data["sum_sold"] / top_traders_data["sum_bought"] < 3 and
                        snipers_data["held_all"] < 80 and
                        snipers_data["no_bought"] < 20 and
                        snipers_data["pnl_loss"] < 30 and
                        token_buyer.token_data.get("info") and
                        token_buyer.token_data["priceChange"]["m5"] > - 15 and
                        token_buyer.token_data["volume"]["m5"] > 500 and
                        total_transfers > 100 and total_transfers < 2500
                    ):
                        mode = Mode.EMULATION
                    else:
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
        
        snipers_table = await page.query_selector("main > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
        await snipers_table
        snipers_table_html = await snipers_table.get_html()    
        
        soup = BeautifulSoup(snipers_table_html, "html.parser")
        snipers_data = {
            "held_all": 0,
            "sold_all": 0,
            "sold_some": 0,
            "bought": "",
            "sold": "",
            "sum_bought": 0,
            "sum_sold" : 0,
            "bought_01_less": 0,
            "bought_5000_more": 0,
            "sold_01_less": 0,
            "sold_5000_more": 0,
            "pnl_5000_more": 0,
            "no_bought": 0,
            "pnl_profit": 0,
            "pnl_loss": 0,
        }
        
        main_div = soup.find("div", recursive=False)
        snipers_divs = main_div.find_all("div", recursive=False)
        bought_lst, sold_lst = [], []
        
        for divs in snipers_divs[1:]:
            snipers_spans = divs.find_all("span")
            bought = await self._get_list_element_by_index(snipers_spans, 5)
            sold = "-"
            pnl = None
            
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
                        
            if pnl:
                if pnl > 0:
                    snipers_data["pnl_profit"] += 1
                else:
                    snipers_data["pnl_loss"] += 1
                    
                if pnl >= 5000:
                    snipers_data["pnl_5000_more"] +=1
                
            if bought != "-":
                bought_lst.append(bought)
                if bought >= 5000:
                    snipers_data["bought_5000_more"] += 1
                elif bought == 0.1:
                    snipers_data["bought_01_less"] += 1
            else:
                bought_lst.append(0)
                
            if sold != "-":
                sold_lst.append(sold)
                if sold >= 5000:
                    snipers_data["sold_5000_more"] += 1
                elif sold == 0.1:
                    snipers_data["sold_01_less"] += 1
            else:
                sold_lst.append(0)
                
        
        snipers_data = await self._update_transactions_data(snipers_data, bought_lst, sold_lst)
 
        return snipers_data
                    
    async def get_top_traders(self, page, mode="monitor") -> dict:
        """
        Получает данные о покупках и продажах из таблицы Top Traders на странице 
        токена. Подсчитывает количество значений в зависимости от диапазона
        и возвращает результат в виде словаря.
        """
        
        await page.wait(2)
        top_traders_table = await page.query_selector("main > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
        await top_traders_table
        top_traders_table_html = await top_traders_table.get_html()

        soup = BeautifulSoup(top_traders_table_html, "html.parser")
        top_traders_data = {
            "bought": "",
            "sold": "",
            "sum_bought": 0,
            "sum_sold" : 0,
            "bought_01_less": 0,
            "bought_5000_more": 0,
            "sold_01_less": 0,
            "sold_5000_more": 0,
            "pnl_5000_more": 0,
            "no_bought": 0,
            "no_sold": 0,
            "pnl_profit": 0,
            "pnl_loss": 0,
        }
        
        main_div = soup.find("div", recursive=False)
        top_traders_divs = main_div.find_all("div", recursive=False)
        bought_lst, sold_lst = [], []
        for divs in top_traders_divs[1:]:
            top_trader_spans = divs.find_all("span")
            
            if mode == "parse":
                top_trader_link = divs.find("a")["href"]
                wallet_address = top_trader_link.split("/")[-1]
                
            bought = await self._get_list_element_by_index(top_trader_spans, 2)
            pnl = None
            
            if bought == "-":
                sold = await self._get_list_element_by_index(top_trader_spans, 3)
                top_traders_data["no_bought"] += 1
                if sold != "-":
                    sold = await self._clear_number(sold)
                    pnl = sold
                else:
                    top_traders_data["no_sold"] += 1  
            else:
                bought = await self._clear_number(bought)
                sold = await self._get_list_element_by_index(top_trader_spans, 7)
                if sold != "-":
                    sold = await self._clear_number(sold)
                    pnl = sold - bought
                else:
                    top_traders_data["no_sold"] += 1
  
            if pnl:
                if pnl > 0:
                    top_traders_data["pnl_profit"] += 1
                else:
                    top_traders_data["pnl_loss"] += 1
                    
                if pnl >= 5000:
                    top_traders_data["pnl_5000_more"] +=1
                
            if bought != "-":
                bought_lst.append(bought)
                if bought >= 5000:
                    top_traders_data["bought_5000_more"] += 1
                elif bought == 0.1:
                    top_traders_data["bought_01_less"] += 1
            else:
                bought_lst.append(0)
                
            if sold != "-":
                sold_lst.append(sold)
                if sold >= 5000:
                    top_traders_data["sold_5000_more"] += 1
                elif sold == 0.1:
                    top_traders_data["sold_01_less"] += 1
            else:
                sold_lst.append(0)

        top_traders_data = await self._update_transactions_data(top_traders_data, bought_lst, sold_lst)
            
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
        
        # try:
        #     mutable_metadata = await rugcheck_page.find("Mutable metadata")
        #     risk_level = "Mutable metadata"
        # except:
        #     pass
            
        await rugcheck_page.close()
        
        return risk_level
                    
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
    
    async def _update_transactions_data(
        self, 
        data: dict, 
        bought_lst: list[float], 
        sold_lst: list[float], 
    ) -> dict:
        """
        Обновляет счетчики в словаре data в соответствии со значениями покупки 
        bought и продажи sold.
        """
        
        data["bought"] = " ".join(map(str, bought_lst))
        data["sold"] = " ".join(map(str, sold_lst))
        data["sum_bought"] = sum(bought_lst)
        data["sum_sold"] = sum(sold_lst)
        data["no_bought"] = bought_lst.count(0)
        data["no_sold"] = sold_lst.count(0)
     
        return data

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
