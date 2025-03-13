import logging
import os
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from ..utils.preprocessing_data import clear_number


logger = logging.getLogger(__name__)

class DexscreenerData:
    def __init__(self, browser, pair):
        self.browser = browser
        self.pair = pair
        self.url = "https://dexscreener.com/solana/" + self.pair

    async def get_transactions_data(self, is_parser=False) -> tuple:
        """
        Открывает страницу токена на DexScreener и сохраняет данные 
        о транзакциях снайперов и топ трейдеров.
        """

        page = await self.browser.get(self.url, new_tab=True)

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
            top_traders_data = await self.get_top_traders(page, is_parser)
        except:
            top_traders_data = None
            
        time.sleep(5)
        try:  
            holders_button = await page.find("Holders")
            await holders_button.click()
            time.sleep(3)
            holders_data = await self.get_holders(page)
            
            total_holders = holders_button.text
            holders_data["total"] = clear_number(total_holders.split(" ")[1][1:-1])
        except:
            holders_data = None

        await page.close()

        return {
            "snipers_data": snipers_data,
            "top_traders_data": top_traders_data,
            "holders_data": holders_data
        }

    async def get_snipers(self, page) -> dict:
        """
        Возвращает словарь с данными о транзакциях из таблицы Snipers на странице 
        токена. 
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
        bought_lst, sold_lst, unrealized_lst = [], [], []
        
        for divs in snipers_divs[1:]:
            snipers_spans = divs.find_all("span")
            
            bought = self._get_list_element_by_index(snipers_spans, 5)
            sold = "-"
            unrealized = self._get_list_element_by_index(divs.find_all("div"), 7)

            operation = self._get_list_element_by_index(snipers_spans, 2)
            if operation == "Held all":
                snipers_data["held_all"] += 1
                if bought != "-":
                    bought = clear_number(bought)
                    
            elif operation == "Sold all" or operation == "Sold some":
                if operation == "Sold all":
                    snipers_data["sold_all"] += 1
                elif operation == "Sold some":
                    snipers_data["sold_some"] += 1
                    
                if bought != "-":
                    bought = clear_number(bought)
                    sold = self._get_list_element_by_index(snipers_spans, 10)
                        
                    if sold != "-":
                        sold = clear_number(sold)
                else:
                    sold = self._get_list_element_by_index(snipers_spans, 6)
                    if sold != "-":
                        sold = clear_number(sold)

            if bought != "-":
                bought_lst.append(bought)
            else:
                bought_lst.append(0)
                
            if sold != "-":
                sold_lst.append(sold)
            else:
                sold_lst.append(0)
                
            if unrealized != '-':
                try:
                    unrealized = clear_number(unrealized)
                except:
                    unrealized = 0
                    
                unrealized_lst.append(unrealized)
            else:
                unrealized_lst.append(0)
 
        snipers_data["bought"] = " ".join(map(str, bought_lst))
        snipers_data["sold"] = " ".join(map(str, sold_lst))
        snipers_data["unrealized"] = " ".join(map(str, unrealized_lst))

        return snipers_data
                    
    async def get_top_traders(self, page, is_parser) -> dict:
        """
        Возвращает словарь с данными о транзакциях из таблицы Top Traders 
        на странице токена. 
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
        bought_lst, sold_lst, unrealized_lst = [], [], []
        wallets_lst = []
        
        for divs in top_traders_divs[1:]:
            top_trader_spans = divs.find_all("span")
            
            if is_parser:
                top_trader_link = divs.find("a")["href"]
                wallet_address = top_trader_link.split("/")[-1]
                wallets_lst.append(wallet_address)
                
            bought = self._get_list_element_by_index(top_trader_spans, 2)

            if bought == "-":
                sold = self._get_list_element_by_index(top_trader_spans, 3)
                if sold != "-":
                    sold = clear_number(sold)
            else:
                bought = clear_number(bought)
                sold = self._get_list_element_by_index(top_trader_spans, 7)
                if sold != "-":
                    sold = clear_number(sold)
                    
            unrealized = self._get_list_element_by_index(divs.find_all("div"), 6)
                
            if bought != "-":
                bought_lst.append(bought)
            else:
                bought_lst.append(0)
                
            if sold != "-":
                sold_lst.append(sold)
            else:
                sold_lst.append(0)
                
            if unrealized != '-':
                try:
                    unrealized = clear_number(unrealized)
                except:
                    unrealized = 0
                    
                unrealized_lst.append(unrealized)
            else:
                unrealized_lst.append(0)

        top_traders_data["bought"] = " ".join(map(str, bought_lst))
        top_traders_data["sold"] = " ".join(map(str, sold_lst))
        top_traders_data["unrealized"] = " ".join(map(str, unrealized_lst))

        if is_parser:
            top_traders_data["wallets"] = " ".join(map(str, wallets_lst))
            
        return top_traders_data
    
    async def get_holders(self, page) -> dict:
        """
        Возвращает словарь с данными о держателях токенов из таблицы Holders 
        на странице токена. 
        """
        
        await page.wait(2)
        holders_table = await page.query_selector(
            "main > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
        )
        await holders_table
        holders_table_html = await holders_table.get_html()
        
        soup = BeautifulSoup(holders_table_html, "html.parser")
        holders_data = {}
        
        main_div = soup.find("div", recursive=False)
        holders_divs = main_div.find_all("div", recursive=False)

        percentages_lst, liquidity_lst = [], []
        for divs in holders_divs[1:-1]:
            percentages_div = divs.find_all("div", recursive=False)[2]

            if len(divs.find_all("div")[2].find_all("span")) == 2:
                liquidity_lst.append(clear_number(percentages_div.text))
            else:
                percentages_lst.append(clear_number(percentages_div.text))
            
        holders_data["percentages"] = " ".join(map(str, percentages_lst))
        holders_data["liquidity"] = " ".join(map(str, liquidity_lst))

        return holders_data
    
    def _get_list_element_by_index(self, lst: list, ind: int) -> str:
        """
        Возвращает элемент списка с индексом ind.
        Если его не существует, то возвращает "0".
        """
        
        try:
            result = lst[ind].text
        except IndexError:
            result = "0"
            
        return result


class DextoolsData:
    def __init__(self, pair, token_address=None):
        self.pair = pair
        self.token_address = token_address
        self.url = "https://www.dextools.io/app/en/solana/pair-explorer/" + self.pair
        self.driver = self._create_driver()
        
    def open_page(self):
        self.driver.get(self.url)
        
        time.sleep(5)
        
    def close_page(self):
        self.driver.close()
        
        time.sleep(5)
        
    def get_holders(self):
        html = self.driver.find_element(By.TAG_NAME, "html")
        html.send_keys(Keys.PAGE_UP)
        html.send_keys(Keys.PAGE_UP)
        
        holders_button = self._get_element(
            by=By.XPATH,
            value="//button[contains(., 'Holders')]"
        )
        holders_button.click()

        time.sleep(5)

        rows = self._get_all_elements(by=By.TAG_NAME, value="datatable-body-row")
        
        holders_data, percentages = {}, []
        for row in rows[:-1]:
            try:
                cells = row.find_elements(By.TAG_NAME, "datatable-body-cell")
            except:
                logger.error("Не удалось прочитать ячейки в строке держателей токена")
                continue
            
            percentages_value = clear_number(cells[1].find_elements(By.TAG_NAME, "div")[1].text)
            
            try:
                maker = row.find_element(By.TAG_NAME, "a").text
            except:
                maker = None
                
            if maker == "5Q544...e4j1":
                holders_data["liquidity"] = percentages_value
            else:
                percentages.append(percentages_value)

        holders_data["percentages"] = " ".join(map(str, percentages))

        total_holders_element = self._get_element("holders-span")
        total_holders_text = self._get_text(total_holders_element)
        holders_data["total"] = int(total_holders_text.split(" ")[-1])
        
        return holders_data
    
    def get_dextscore(self):
        dextscore_element = self._get_element(
            by=By.XPATH, 
            value="/div[contains(@class, 'dext-value')]/strong"
        )
        
        dextscore = self._get_text(dextscore_element)
        
        return dextscore
           
    def get_top_traders(self):
        top_traders_button = self._get_element(
            by=By.XPATH, 
            value="//button[contains(., 'Top Traders')]",
            timeout=10,
        )
        top_traders_button.click()
        time.sleep(5)

        table = self._get_element("datatable-body")

        action = ActionChains(self.driver)
        action.move_to_element(table).perform()
        
        max_height = self.driver.execute_script("return arguments[0].scrollHeight", table)
        
        bought, sold, unrealized, speed, makers = [], [], [], [], []
        for i in range(0, max_height, 500):
            self.driver.execute_script(f"arguments[0].scrollTop = {i}", table)
            
            time.sleep(1)
            
            rows = self._get_all_elements(by=By.TAG_NAME, value="datatable-body-row")
            
            if not rows:
                continue
            
            for each_row in rows:
                try:
                    cells = each_row.find_elements(By.TAG_NAME, "datatable-body-cell")
                except:
                    logger.error("Не удалось прочитать ячейки в строке топовых транзакций")
                    continue
                
                try:
                    maker = cells[1].find_element(By.TAG_NAME, "span").text
                except:
                    logger.error("Не удалось определить топовый кошелёк")
                    continue
                
                if maker in makers:
                    continue

                try:
                    value = cells[7].find_element(By.TAG_NAME, "span").text
                    clear_value = clear_number(value)
                    if clear_value == -1:
                        bought.append("0")
                    else:
                        bought.append(clear_value)
                except:
                    bought.append("0")
                    
                try:
                    value = cells[8].find_element(By.TAG_NAME, "span").text
                    clear_value = clear_number(value)
                    if clear_value == -1:
                        sold.append("0")
                    else:
                        sold.append(clear_value)
                except:
                    sold.append("0")
                    
                try:
                    each_row.find_element(
                        By.XPATH, 
                        ".//app-maker-speed/div/fa-icon[contains(@class, 'medium')]"
                    ).text
                    speed.append("medium")
                except:
                    speed.append("fast")
                
                try:
                    value = cells[5].find_element(By.TAG_NAME, "div").text
                    clear_value = clear_number(value)
                    if clear_value == -1:
                        unrealized.append("0")
                    else:
                        unrealized.append(clear_value)
                except:
                    unrealized.append("0")  
                    
                makers.append(maker)
                        
            time.sleep(1)

        top_traders_data = {
            "bought": " ".join(map(str, bought)),
            "sold": " ".join(map(str, sold)),
            "unrealized": " ".join(map(str, unrealized)),
            "speed": " ".join(map(str, speed)),
        }
        
        return top_traders_data
    
    def get_trade_history(self):
        html = self.driver.find_element(By.TAG_NAME, "html")
        html.send_keys(Keys.PAGE_UP)
        
        trade_history_button = self._get_element(
            by=By.XPATH, 
            value="//button[contains(., 'Trade History')]"
        )
        trade_history_button.click()
        
        time.sleep(5)
        
        html.send_keys(Keys.PAGE_DOWN)

        table = self._get_element("datatable-body") 
        
        action = ActionChains(self.driver)
        action.move_to_element(table).perform()

        keys, date, operations, prices, trades_sum, makers, trades_for_maker = ([] for _ in range(7))
        
        max_height = self.driver.execute_script("return arguments[0].scrollHeight", table)
        
        if max_height > 12000:
            max_height = 12000
        
        for i in range(0, 10000, 650):
            self.driver.execute_script(f"arguments[0].scrollTop = {i}", table)
            
            time.sleep(1)
            
            rows = self._get_all_elements(by=By.TAG_NAME, value="datatable-body-row")
            
            if not rows:
                continue
            
            for each_row in rows:
                try:
                    cells = each_row.find_elements(By.TAG_NAME, "datatable-body-cell")
                except:
                    logger.error("Не удалось прочитать ячейки в строке истории транзакций")
                    continue

                if len(cells) < 9:
                    continue
                
                maker_value = self._get_text_by_index(cells, 8)
                date_value = self._get_text_by_index(cells, 0)
                
                key = f"{date_value}: {maker_value}"          
                if key in keys:
                    continue
                
                date.append(date_value)
                
                operation_value = self._get_text_by_index(cells, 1)
                operations.append(operation_value)
                
                price_value = clear_number(self._get_text_by_index(cells, 2))
                prices.append(price_value)
                
                trade_sum_value = clear_number(self._get_text_by_index(cells, 3))
                trades_sum.append(trade_sum_value)
                
                makers.append(maker_value)
                
                trades_for_maker_value = int(clear_number(self._get_text_by_index(cells, 9)))
                trades_for_maker.append(trades_for_maker_value) 
                
                keys.append(key)
                
        transactions_element = self._get_element("pair-explorer-footer__transactions") 
        try:
            transactions = self._get_text(transactions_element).split(" ")[-2]
        except:
            transactions = 0

        trade_history_data = {
            "prices": " ".join(map(str, prices)),
            "date": ",".join(map(str, date)),
            "operations": " ".join(map(str, operations)),
            "trades_sum": " ".join(map(str, trades_sum)),
            "trades_makers": " ".join(map(str, makers)),
            "trades_for_maker": " ".join(map(str, trades_for_maker)),
            "transactions": transactions
        }
        
        return trade_history_data

    def _create_driver(self):
        options = Options()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_directory = os.path.join(script_dir, 'users')
        user_directory = os.path.join(base_directory, f'user_1')

        options.add_argument(f'user-data-dir={user_directory}')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')

        driver = webdriver.Chrome(options=options)
        ua = UserAgent(browsers='Chrome', os='Windows', platforms='desktop', fallback="Edge").random
        stealth(driver=driver,
                user_agent=ua,
                languages=["ru-RU", "ru"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                run_on_insecure_origins=True
                )

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            'source': '''
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''
        })
        return driver
    
    def _get_all_elements(self, value: str, timeout: int=15, by=By.CLASS_NAME):
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except:
            elements = None
            logger.error(f"Не удалось найти элементы {value}")
        
        return elements
    
    def _get_element(self, value: str, timeout: int=15, by=By.CLASS_NAME): 
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except:
            element = None
            logger.error(f"Не удалось найти элемент {value}")
            
        return element
    
    def _get_text(self, element, element_name=""):
        try:
            text = element.text
        except:
            text = "0"
            logger.error(f"Не удалось получить текст элемента {element_name}")
        
        return text
    
    def _get_text_by_index(self, element, i, element_name=""):
        try:
            text = element[i].text
        except:
            text = "0"
            logger.error(
                f"Не удалось получить текст элемента {element_name} по индексу {i}"
            )
        
        return text
