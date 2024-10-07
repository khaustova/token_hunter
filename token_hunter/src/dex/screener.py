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
    
    async def watch_token(self, filter: str):
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
                    
                    await link.click()
                    await self.browser.wait(3)
                    
                    
                    try:
                        snipers_button = await dex_page.find("Snipers")
                        await snipers_button.click()
                        dex_page.wait(5)
                    except:
                        return
 
                    # risk_level = await self.rugcheck(token_checker.token_address)
                    # logger.info(f"Уровень риска токена {token_checker.token_name}: {risk_level}")
                    
                    # if risk_level == None:
                    #     continue
                    # elif risk_level != "Good":
                    #     black_list.append(link)
                        #continue
  
                    # await dex_page.wait(2)
                    # total_transfers = await self.get_total_transfers(token_checker.token_address)
                    # if not token_checker.check_transfers(total_transfers):
                    #     black_list.append(link)
                    #     #continue
                    
                    # await self.browser.get('https://api-v2.solscan.io/v2/token/transfer/export?address=' + token_checker.token_address, new_tab=True)
                    
                    # token_buyer = TokenBuyer(pair, total_transfers)
                    # if token_buyer.check_token() or 1:
                    # #     mode = Mode.EMULATION
                    # # else:
                    #     mode = Mode.DATA_COLLECTION
                    
                    try:
                        await link.click()
                        await self.browser.wait(3)
                    except:
                        await self.browser.wait(3)
                        continue
                    
                    snipers_button = await dex_page.find("Snipers")
                    await snipers_button.click()
                    
                    await dex_page.wait(3)
                    
                    top_snipers_data = await self.get_snipers(dex_page)

                    top_traders_button = await dex_page.find("Top Traders")
                    await top_traders_button.click()
                    
                    await dex_page.wait(3)
                    
                    top_traders_data = await self.get_top_traders(dex_page)

                    #await sync_to_async(token_buyer.buy_token)(mode)
                     
                    # transactions_list.append(link)
                    
                    await dex_page.back()
                    
                    return
                    
            await self.browser.wait(10)
        
    async def parse_top_traders(self, filter: str="", pages: int=1):
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
                    
                    
    async def get_snipers(self, page):
        snipers_table = await page.select("main > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
        snipers_table_html = await snipers_table.get_html()
            
        soup = BeautifulSoup(snipers_table_html, "html.parser")
        snipers_data = {
            "held_all": 0,
            "sold_all": 0,
            "sold_some": 0,
            "bought_100_less": 0,
            "bought_100_500": 0,
            "bought_500_1000": 0,
            "bought_1000_2500": 0,
            "bought_2500_5000": 0,
            "bought_5000_more": 0,
            "sold_100_less": 0,
            "sold_100_500": 0,
            "sold_500_1000": 0,
            "sold_1000_2500": 0,
            "sold_2500_5000": 0,
            "sold_5000_more": 0,
            "pnl_100_less": 0,
            "pnl_100_500": 0,
            "pnl_500_1000": 0,
            "pnl_1000_2500": 0,
            "pnl_2500_5000": 0,
            "pnl_5000_more": 0,
            "no_bought": 0,
            "pnl_profit": 0,
            "pnl_loss": 0,
        }
        
        
        main_div = soup.find("div", recursive=False)
        snipers_divs = main_div.find_all("div", recursive=False)
        for divs in snipers_divs[1:]:
            snipers_spans = divs.find_all("span")
            bought = snipers_spans[5].text
            sold = "-"
            if snipers_spans[2].text == "Held all":
                snipers_data["held_all"] += 1
                if bought != "-":
                    bought = await self.clear_number(bought)
            elif snipers_spans[2].text == "Sold all" or snipers_spans[2].text == "Sold some":
                if snipers_spans[2].text == "Sold all":
                    snipers_data["sold_all"] += 1
                elif snipers_spans[2].text == "Sold some":
                    snipers_data["sold_some"] += 1
                    
                if bought != "-":
                    bought = await self.clear_number(bought)
                    sold = await self.clear_number(snipers_spans[10].text)
                    pnl = sold - float(bought)
                else:
                    sold = await self.clear_number(snipers_spans[6].text)
                    pnl = sold
                    snipers_data["no_bought"] += 1
                    
                if pnl > 0:
                    snipers_data["pnl_profit"] += 1
                else:
                    snipers_data["pnl_loss"] += 1
                    
            snipers_data = await self.count_costs(snipers_data, bought, sold, pnl)
            
        return snipers_data
                    
    async def get_top_traders(self, page):
        top_traders_table = await page.select("main > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)")
        top_traders_table_html = await top_traders_table.get_html()
        
        soup = BeautifulSoup(top_traders_table_html, "html.parser")
        top_traders_data = {
            "bought_100_less": 0,
            "bought_100_500": 0,
            "bought_500_1000": 0,
            "bought_1000_2500": 0,
            "bought_2500_5000": 0,
            "bought_5000_more": 0,
            "sold_100_less": 0,
            "sold_100_500": 0,
            "sold_500_1000": 0,
            "sold_1000_2500": 0,
            "sold_2500_5000": 0,
            "sold_5000_more": 0,
            "pnl_100_less": 0,
            "pnl_100_500": 0,
            "pnl_500_1000": 0,
            "pnl_1000_2500": 0,
            "pnl_2500_5000": 0,
            "pnl_5000_more": 0,
            "no_bought": 0,
            "pnl_profit": 0,
            "pnl_loss": 0,
        }
        
        main_div = soup.find("div", recursive=False)
        top_traders_divs = main_div.find_all("div", recursive=False)
        for divs in top_traders_divs[1:]:
            top_traders_spans = divs.find_all("span")
            bought = top_traders_spans[2].text
            if bought == "-":
                top_traders_data["no_bought"] += 1
                sold = await self.clear_number(top_traders_spans[3].text)
                pnl = sold
            else:
                bought = await self.clear_number(bought)
                if sold != "-":
                    sold = await self.clear_number(top_traders_spans[7].text)
                    pnl = sold - bought
            print(bought, sold)
            
            if pnl > 0:
                top_traders_data["pnl_profit"] += 1
            else:
                top_traders_data["pnl_loss"] += 1
                    
            top_traders_data = await self.count_costs(top_traders_data, bought, sold, pnl)
            
        return top_traders_data
                    
    async def clear_number(self, number_str: str):
        number_str = number_str.lstrip("0").lstrip("$")
        number_str = number_str.replace(",", "").replace(">", "").replace("<", "").replace("$", "")
        if "K" in number_str or "M" in number_str:
            number_str = number_str.replace(".", "").replace("K", "000").replace("M", "000000")
        number = float(number_str)
        
        return number

    async def count_costs(self, data, bought, sold, pnl):
        if bought != "-":      
            if bought >= 0 and bought < 100:
                data["bought_100_less"] += 1
            elif bought >= 100 and bought < 500:
                data["bought_100_500"] += 1
            elif bought >= 500 and bought < 1000:
                data["bought_500_1000"] += 1
            elif bought >= 1000 and bought < 2500:
                data["bought_1000_2500"] += 1
            elif bought >= 2500 and bought < 5000:
                data["bought_2500_5000"] += 1
            elif bought >= 5000:
                data["bought_5000_more"] += 1
                
        if sold != "-":      
            if sold >= 0 and sold < 100:
                data["sold_100_less"] += 1
            elif sold >= 100 and sold < 500:
                data["sold_100_500"] += 1
            elif sold >= 500 and sold < 1000:
                data["sold_500_1000"] += 1
            elif sold >= 1000 and sold < 2500:
                data["sold_1000_2500"] += 1
            elif sold >= 2500 and sold < 5000:
                data["sold_2500_5000"] += 1
            elif sold >= 5000:
                data["sold_5000_more"] += 1
                
        if pnl >= 0 and pnl < 100:
            data["pnl_100_less"] += 1
        elif pnl >= 100 and pnl < 500:
            data["pnl_100_500"] += 1
        elif pnl >= 500 and pnl < 1000:
            data["pnl_500_1000"] += 1
        elif pnl >= 1000 and pnl < 2500:
            data["pnl_1000_2500"] += 1
        elif pnl >= 2500 and pnl < 5000:
            data["pnl_2500_5000"] += 1
        elif pnl >= 5000:
            data["pnl_5000_more"] += 1
                
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
            
    async def rugcheck(self, token_address):
        """
        Возвращает уровень риска токена token_address с rugcheck.xyz. 
        """
        
        rugcheck_page = await self.browser.get(
            "https://rugcheck.xyz/tokens/" + token_address, 
            new_tab=True
        )
        await rugcheck_page
        
        time.sleep(7)
       
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
    dex_worker = DexScreener(browser)
    await dex_worker.watch_token(filter)


async def run_dexscreener_parser(filter, pages):  
    """
    Инициализирует браузер и запускает парсинг топов кошельков DesScreener.
    """  
    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    dex_worker = DexScreener(browser)
    await dex_worker.parse_top_traders(filter, pages)
