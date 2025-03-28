import logging
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from nodriver.core.browser import Browser
from nodriver.core.tab import Tab
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from token_hunter.src.utils.preprocessing_data import (
    clear_number,
    get_text_list_element_by_index
)

logger = logging.getLogger(__name__)


class DexScreenerData:
    """Класс для получения данных о транзакциях и держателях токенов на DEX Screener.

    Note:
        Использует библиотеку nodriver и требует ручное прохождение проверки Cloudflare 
        примерно 1 раз в 1.5 суток, поэтому при инициализации браузера нельзя использовать headless.

    Attributes:
        browser: Экземпляр браузера Chrome.
        pair: Адрес пары токена.
        url: Ссылка на страницу токена на DEX Screener.
    """

    def __init__(self, browser: Browser, pair: str):
        """Инициализирует экземпляр DexScreenerData.
        
        Args:
            browser: Экземпляр браузера Chrome.
            pair: Адрес пары токена.
        """
        self.browser = browser
        self.pair = pair
        self.url = "https://dexscreener.com/solana/" + self.pair

    async def get_dex_data(self, is_parser: bool=False) -> dict:
        """Открывает страницу токена на DEX Screener и сохраняет данные о транзакциях
        снайперов, топовых кошельков и о держателях токенов.

        Args:
            is_parser: Флаг, указывающий, нужно ли собирать подробные данные о топовых кошельках. 
                Используется для парсинга топовых кошельков. По умолчанию False.

        Returns:
            Словарь с данными о транзакциях и держателях токенов.
        """
        page = await self.browser.get(self.url, new_tab=True)

        time.sleep(5)
        await page.wait(10)

        if is_parser:
            try:
                top_traders_button = await page.find("Top Traders")
                await top_traders_button.click()
                time.sleep(3)
                top_traders_data = await self.get_top_traders(page, is_parser)
            except Exception:
                top_traders_data = None

            return top_traders_data

        try:
            snipers_button = await page.find("Snipers")
            await snipers_button.click()
            time.sleep(3)
            snipers_data = await self.get_snipers(page)
        except Exception:
            snipers_data = None

        time.sleep(5)
        try:
            top_traders_button = await page.find("Top Traders")
            await top_traders_button.click()
            time.sleep(3)
            top_traders_data = await self.get_top_traders(page, is_parser)
        except Exception:
            top_traders_data = None

        time.sleep(5)
        try:
            holders_button = await page.find("Holders")
            await holders_button.click()
            time.sleep(3)
            holders_data = await self.get_holders(page)

            total_holders = holders_button.text
            holders_data["total"] = clear_number(total_holders.split(" ")[1][1:-1])
        except Exception:
            holders_data = None

        await page.close()

        return {
            "snipers_data": snipers_data,
            "top_traders_data": top_traders_data,
            "holders_data": holders_data
        }

    async def get_snipers(self, page: Tab) -> dict:
        """Получает данные о транзакциях снайперов из таблицы Snipers на странице токена.

        Args:
            page: Страница токена, на которой открыта таблица со снайперами.

        Returns:
            Словарь с данными о транзакциях снайперов.
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

            bought = get_text_list_element_by_index(snipers_spans, 5)
            sold = "-"
            unrealized = get_text_list_element_by_index(divs.find_all("div"), 7)

            operation = get_text_list_element_by_index(snipers_spans, 2)
            if operation == "Held all":
                snipers_data["held_all"] += 1
                if bought != "-":
                    bought = clear_number(bought)

            elif operation in ("Sold all", "Sold some"):
                if operation == "Sold all":
                    snipers_data["sold_all"] += 1
                elif operation == "Sold some":
                    snipers_data["sold_some"] += 1

                if bought != "-":
                    bought = clear_number(bought)
                    sold = get_text_list_element_by_index(snipers_spans, 10)

                    if sold != "-":
                        sold = clear_number(sold)
                else:
                    sold = get_text_list_element_by_index(snipers_spans, 6)
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
                except Exception:
                    unrealized = 0

                unrealized_lst.append(unrealized)
            else:
                unrealized_lst.append(0)

        snipers_data["bought"] = " ".join(map(str, bought_lst))
        snipers_data["sold"] = " ".join(map(str, sold_lst))
        snipers_data["unrealized"] = " ".join(map(str, unrealized_lst))

        return snipers_data

    async def get_top_traders(self, page: Tab, is_parser: bool) -> dict:
        """Получает данные о транзакциях топовых кошельков из таблицы Top Traders на странице токена.

        Args:
            page: Страница токена, на которой открыта таблица с топовыми кошельками.
            is_parser: Флаг, указывающий, нужно ли собирать адреса кошельков. 
                Используется для парсинга топовых кошельков.

        Returns:
            Словарь с данными о транзакциях топовых кошельков.
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
        makers = []

        for divs in top_traders_divs[1:]:
            top_trader_spans = divs.find_all("span")

            if is_parser:
                top_trader_link = divs.find("a")["href"]
                maker = top_trader_link.split("/")[-1]
                makers.append(maker)

            bought = get_text_list_element_by_index(top_trader_spans, 2)

            if bought == "-":
                sold = get_text_list_element_by_index(top_trader_spans, 3)
                if sold != "-":
                    sold = clear_number(sold)
            else:
                bought = clear_number(bought)
                sold = get_text_list_element_by_index(top_trader_spans, 7)
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

            unrealized = get_text_list_element_by_index(divs.find_all("div"), 6)
            if unrealized != '-':
                try:
                    unrealized = clear_number(unrealized)
                except Exception:
                    unrealized = 0

                unrealized_lst.append(unrealized)
            else:
                unrealized_lst.append(0)

        top_traders_data["bought"] = " ".join(map(str, bought_lst))
        top_traders_data["sold"] = " ".join(map(str, sold_lst))
        top_traders_data["unrealized"] = " ".join(map(str, unrealized_lst))

        if is_parser:
            top_traders_data["makers"] = " ".join(map(str, makers))

        return top_traders_data

    async def get_holders(self, page: Tab) -> dict:
        """Получает данные о держателях токенов из таблицы Holders на странице токена.

        Args:
            page: Страница токена, на которой открыта таблица с держателями токенов.

        Returns:
            Словарь с данными о держателях токенов.
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


class DexToolsData:
    """Класс для получения данных о транзакциях и держателях токенов на DEXTools.

    Note:
        Использует библиотеку selenium и не требует ручное прохождение проверки Cloudflare, 
        поэтому разрешается использование headless.

    Attributes:
        pair: Адрес пары токена.
        token_address: Адрес токена.
        url: Ссылка на страницу токена на DEXTools.
        driver: Созданный и настроенный экзепмляр веб-драйвера Selenium.
    """

    def __init__(self, pair: str, token_address: str | None=None):
        """Инициализирует экземпляр DexToolsData.
        
        Args:
            pair: Адрес пары токена.
            token_address: Адрес токена.
        """
        self.pair = pair
        self.token_address = token_address
        self.url = "https://www.dextools.io/app/en/solana/pair-explorer/" + self.pair
        self.driver = self._create_driver()

    def get_dex_data(self, is_parser: bool=False):
        """Открывает страницу токена на DEXTools и сохраняет данные о транзакциях
        снайперов, топовых кошельков и о держателях токенов.

        Args:
            is_parser: Флаг, указывающий, нужно ли собирать подробные данные о топовых кошельках. 
                Используется для парсинга топовых кошельков. По умолчанию False.

        Returns:
            Словарь с данными о транзакциях и держателях токенов.
        """
        self.driver.get(self.url)
        time.sleep(5)

        if is_parser:
            top_traders_data = self.get_top_traders(is_parser)
            self.driver.quit()
            return top_traders_data

        result = {}
        result["dextscore"] = self.get_dextscore()
        result["top_traders_data"] = self.get_top_traders(is_parser)
        result["holders_data"] = self.get_holders()
        result["trade_history_data"] = self.get_trade_history()

        self.driver.quit()

        return result

    def get_holders(self) -> dict:
        """Получает данные о держателях токенов из таблицы Holders на странице токена.

        Returns:
            Словарь с данными о держателях токенов.
        """
        html = self.driver.find_element(By.TAG_NAME, "html")
        html.send_keys(Keys.PAGE_UP)
        html.send_keys(Keys.PAGE_UP)

        holders_button = self._get_element(
            by=By.XPATH,
            value="//button[contains(., 'Holders')]"
        )

        try:
            holders_button.click()
        except Exception:
            return None

        time.sleep(5)

        rows = self._get_all_elements(by=By.TAG_NAME, value="datatable-body-row")

        holders_data, percentages = {}, []

        if not rows:
            return holders_data

        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "datatable-body-cell")
            except Exception:
                logger.debug("Не удалось прочитать ячейки в строке держателей токена")
                continue

            percentages_value = clear_number(cells[1].find_elements(By.TAG_NAME, "div")[1].text)

            try:
                maker = row.find_element(By.TAG_NAME, "a").text
            except Exception:
                maker = None

            if maker == "5Q544...e4j1":
                holders_data["liquidity"] = percentages_value
            else:
                percentages.append(percentages_value)

        holders_data["percentages"] = " ".join(map(str, percentages[:-1]))

        total_holders_element = self._get_element("holders-span")
        total_holders_text = self._get_text(total_holders_element)
        holders_data["total"] = int(total_holders_text.split(" ")[-1])

        return holders_data

    def get_dextscore(self) -> str:
        """Получает значение DextScore для токена.

        Returns:
            Значение DextScore.
        """
        dextscore_element = self._get_element(
            by=By.XPATH,
            value="/div[contains(@class, 'dext-value')]/strong"
        )

        dextscore = self._get_text(dextscore_element)

        return dextscore

    def get_top_traders(self, is_parser: bool) -> dict:
        """Получает данные о транзакциях топовых кошельков из таблицы Top Traders на странице токена.

        Args:
            page: Страница токена, на которой открыта таблица с топовыми кошельками.
            is_parser: Флаг, указывающий, нужно ли собирать адреса кошельков. 
                Используется для парсинга топовых кошельков.

        Returns:
            Словарь с данными о транзакциях топовых кошельков.
        """
        top_traders_button = self._get_element(
            by=By.XPATH,
            value="//button[contains(., 'Top Traders')]",
            timeout=10,
        )

        try:
            top_traders_button.click()
        except Exception:
            return None

        time.sleep(5)

        table = self._get_element("datatable-body")
        
        if not table:
            return None

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
                except Exception:
                    logger.debug("Не удалось прочитать ячейки в строке топовых транзакций")
                    continue

                try:
                    maker = cells[1].find_element(By.TAG_NAME, "span").text
                    
                    if is_parser:
                        maker_href = cells[1].find_element(By.TAG_NAME, "a").get_attribute("href")
                        maker = maker_href.split("/")[-1]
                except Exception:
                    logger.debug("Не удалось определить топовый кошелёк")
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
                except Exception:
                    bought.append("0")

                try:
                    value = cells[8].find_element(By.TAG_NAME, "span").text
                    clear_value = clear_number(value)
                    if clear_value == -1:
                        sold.append("0")
                    else:
                        sold.append(clear_value)
                except Exception:
                    sold.append("0")

                try:
                    is_speed = each_row.find_element(
                        By.XPATH,
                        ".//app-maker-speed/div/fa-icon[contains(@class, 'medium')]"
                    ).text
                    speed.append("medium")
                except Exception:
                    speed.append("fast")

                try:
                    value = cells[5].find_element(By.TAG_NAME, "div").text
                    clear_value = clear_number(value)
                    if clear_value == -1:
                        unrealized.append("0")
                    else:
                        unrealized.append(clear_value)
                except Exception:
                    unrealized.append("0")

                makers.append(maker)

            time.sleep(1)

        top_traders_data = {
            "bought": " ".join(map(str, bought)),
            "sold": " ".join(map(str, sold)),
            "unrealized": " ".join(map(str, unrealized)),
            "speed": " ".join(map(str, speed)),
        }

        if is_parser:
            top_traders_data["makers"] = " ".join(map(str, makers))

        return top_traders_data

    def get_trade_history(self):
        """Получает историю последних транзакций из таблицы Trade History на странице токена.

        Returns:
            Словарь с данными о последних транзакциях.
        """
        html = self.driver.find_element(By.TAG_NAME, "html")
        html.send_keys(Keys.PAGE_UP)

        trade_history_button = self._get_element(
            by=By.XPATH,
            value="//button[contains(., 'Trade History')]"
        )

        try:
            trade_history_button.click()
        except Exception:
            return None

        time.sleep(5)

        html.send_keys(Keys.PAGE_DOWN)
        table = self._get_element("datatable-body")

        if not table:
            return None

        action = ActionChains(self.driver)
        action.move_to_element(table).perform()

        keys = []
        date, operations, prices, trades_sum, makers, trades_for_maker = ([] for _ in range(6))

        for i in range(0, 15000, 650):
            self.driver.execute_script(f"arguments[0].scrollTop = {i}", table)

            time.sleep(1)

            rows = self._get_all_elements(by=By.TAG_NAME, value="datatable-body-row")

            if not rows:
                continue

            for each_row in rows:
                try:
                    cells = each_row.find_elements(By.TAG_NAME, "datatable-body-cell")
                except Exception:
                    logger.debug("Не удалось прочитать ячейки в строке истории транзакций")
                    continue

                if len(cells) < 9:
                    continue

                maker_value = get_text_list_element_by_index(cells, 8)
                date_value = get_text_list_element_by_index(cells, 0)

                key = f"{date_value}: {maker_value}"
                if key in keys:
                    continue

                date.append(date_value)

                operation_value = get_text_list_element_by_index(cells, 1)
                operations.append(operation_value)

                price_value = clear_number(get_text_list_element_by_index(cells, 2))
                prices.append(price_value)

                trade_sum_value = clear_number(get_text_list_element_by_index(cells, 3))
                trades_sum.append(trade_sum_value)

                makers.append(maker_value)

                trades_for_maker_value = int(clear_number(get_text_list_element_by_index(cells, 9)))
                trades_for_maker.append(trades_for_maker_value)

                keys.append(key)

        transactions_element = self._get_element("pair-explorer-footer__transactions")

        try:
            transactions = self._get_text(transactions_element).split(" ")[-2]
        except Exception:
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

    def _create_driver(self) -> WebDriver:
        """Создает и настраивает экземпляр веб-драйвера Selenium.

        Returns:
            Настроенный экземпляр веб-драйвера.
        """
        options = Options()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        ua = UserAgent(browsers="Chrome", os="Windows", platforms="desktop", fallback="Edge").random
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

    def _get_all_elements(
        self,
        value: str,
        timeout: int=15,
        by: str=By.CLASS_NAME
    ) -> list[WebElement] | None:
        """Ищет все элементы на странице по указанному локатору.

        Args:
            value: Значение локатора.
            timeout: Время ожидания. По умолчанию 15.
            by: Тип локатора. По умолчанию By.CLASS_NAME.

        Returns:
            Список найденных элементов или None, если элементы не найдены.
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except Exception:
            elements = None
            logger.debug("Не удалось найти элементы %s", value)

        return elements

    def _get_element(
        self,
        value: str,
        timeout: int=15,
        by: str=By.CLASS_NAME
    ) -> WebElement | None:
        """Ищет элемент на странице по указанному локатору.

        Args:
            value: Значение локатора.
            timeout: Время ожидания. По умолчанию 15.
            by: Тип локатора. По умолчанию By.CLASS_NAME.

        Returns:
            Найденный элемент или None, если элемент не найден.
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception:
            element = None
            logger.debug("Не удалось найти элемент %s", value)

        return element

    def _get_text(self, element: WebElement, element_name: str="элемента") -> str:
        """Возвращает текст элемента.
        
        Args:
            element: Найденный элемент.
            element_name: Имя элемента. Используется для логирования исключения.
                По умолчание "элемента".
                
        Return:
            Текст элемента или "0", если не удалось получить текст. 
        """
        try:
            text = element.text
        except Exception:
            text = "0"
            logger.debug("Не удалось получить текст %s", element_name)

        return text
