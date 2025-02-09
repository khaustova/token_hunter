import logging
import os
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
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

        await page.close()
        
        return {
            "snipers_data": snipers_data,
            "top_traders_data": top_traders_data
        }

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
            bought = self._get_list_element_by_index(snipers_spans, 5)
            sold = "-"
            
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
                
        
        snipers_data["bought"] = " ".join(map(str, bought_lst))
        snipers_data["sold"] = " ".join(map(str, sold_lst))
 
        return snipers_data
                    
    async def get_top_traders(self, page, is_parser) -> dict:
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
        
        if is_parser:
            top_traders_data["wallets"] = " ".join(map(str, wallets_lst))
            
        return top_traders_data
    
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
    def __init__(self, pair):
        self.pair = pair
        self.url = "https://www.dextools.io/app/en/solana/pair-explorer/" + self.pair
        self.driver = self._create_driver()
        
    def get_transactions_data(self):
        self.driver.get(self.url)
        time.sleep(5)
        
        self.driver.find_element(By.XPATH, "//button[contains(., 'Top Traders')]").click()

        time.sleep(5)

        table = self.driver.find_element(By.CLASS_NAME, "datatable-body")
        
        action = ActionChains(self.driver)
        action.move_to_element(table).perform()
        
        max_height = self.driver.execute_script("return arguments[0].scrollHeight", table)
        
        table_rows = self.driver.find_elements(By.TAG_NAME, "datatable-body-row")
        bought, sold, unrealized, speed = [], [], [], []
        makers = []
        for i in range(0, max_height, 500):
            self.driver.execute_script(f"arguments[0].scrollTop = {i}", table)
            time.sleep(1)
            rows = self.driver.find_elements(By.TAG_NAME, "datatable-body-row")
            
            for each_row in rows:
                maker = each_row.find_element(By.XPATH, ".//datatable-body-cell[2]/div/app-maker-address/div/a[1]/span").text
                if maker in makers:
                    continue
                
                else:
                    try:
                        bought.append(each_row.find_element(By.XPATH, ".//datatable-body-cell[8]/div/div/span").text)
                    except:
                        bought.append("0")
                        
                    try:
                        sold.append(each_row.find_element(By.XPATH, ".//datatable-body-cell[9]/div/div/span").text)
                    except:
                        sold = "0"
                        sold.append("0")
                        
                    try:
                        each_row.find_element(By.XPATH, ".//app-maker-speed/div/fa-icon[contains(@class, 'medium')]").text
                        speed.append("medium")
                    except:
                        speed.append("fast")
                    
                    try:
                        unrealized.append(each_row.find_element(By.XPATH, ".//datatable-body-row/div[2]/datatable-body-cell[6]/div").text)
                    except:
                        unrealized.append("0") 
                    
            time.sleep(1)
            
        dextscore = self.driver.find_element(By.XPATH, "//div[contains(@class, 'dext-value')]/strong").text
        
        top_traders_data = {
            "bought": " ".join(bought),
            "sold": " ".join(sold),
            "unrealized": " ".join(unrealized),
            "speed": " ".join(speed),
        }
        
        return {
            "top_traders_data": top_traders_data,
            "dextscore": dextscore,
        }

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
        ua = UserAgent(browsers='Chrome', os='Windows', platforms='desktop', fallback="Chrome")
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
