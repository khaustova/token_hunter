import asyncio
import time
import logging
import nodriver as uc
import pandas as pd
import random
from asgiref.sync import sync_to_async
from django.conf import settings
from bs4 import BeautifulSoup
from nodriver.core.config import Config
from .coin_worker import buy_coin, CoinChecker
from ..models import TopTrader


logger = logging.getLogger(__name__)


class DexWorker():
    def __init__(self, browser):
        self.browser = browser
        
    async def watch_coin(self, filter: str):
        # await self._get_2captcha_api_key()
        dex_page = await self.browser.get('https://dexscreener.com/solana' + filter)
        await asyncio.sleep(10)
        visited_links, black_list = [], []

        while True:
            all_links = await dex_page.query_selector_all("a.ds-dex-table-row")

            links = [item for item in all_links if item not in visited_links]
            await asyncio.sleep(5)
            
            if links:
                for link in links:
                    pair = link.attributes[-1].split("/")[-1]
                    print(pair)
                    coin_checker = CoinChecker(pair)
                    first_check_coin = coin_checker.check_coin()
                    if first_check_coin:
                        logger.info(f"Монета {coin_checker.coin_name} прошла первый этап проверки")
                        await dex_page.wait(15)
                        risk_level = await self.rugcheck_coin(coin_checker.coin_address)
                        logger.info(f"Уровень риска монеты {coin_checker.coin_name}: {risk_level}")
                        if risk_level != "Good":
                            black_list.append(link)
                            await self.browser.wait(3)
                            
                            continue
                    else:
                        logger.info(f"Монета {coin_checker.coin_name} не прошла первый этап проверки")
                        black_list.append(link)
                        await self.browser.wait(3)
                            
                        continue
                        
                    await sync_to_async(buy_coin)(
                        coin_checker.coin_name, 
                        coin_checker.coin_address
                    )
                    
                    await dex_page.wait(2)

                    # active_tasks = get_active_tasks()
 
                    # await dex_page.back()
                    
                    await self.browser.wait(5)

            await self.browser.wait(10)
        
            
    async def parse_top_traders(self, filter: str="", pages: int=1):
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
                    is_visited = await self.check_visited_link(pair)
                    if is_visited:
                        logger.debug(f"Монета на странице уже проанализирована")
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
                                        
                    coin_link = await dex_page.query_selector_all("a.custom-isf5h9")
                    coin_address = coin_link[1].attributes[-1].split("/")[-1]
                    
                    await dex_page.wait(10)
                    
                    risk_level = await self.rugcheck_coin(coin_address)
                    logger.info(f"Уровень риска монеты {coin_address}: {risk_level}")    
                    if risk_level != "Good":
                        await dex_page.back()
                        await dex_page
                        continue

                    page_sourse = await dex_page.get_content()
                    soup = BeautifulSoup(page_sourse, "html.parser")
                    await sync_to_async(self.save_top_traders)(pair, soup)
                    
                    await asyncio.sleep(5)

                    await dex_page.back()
                    
    
    def save_top_traders(self, pair: str, soup: BeautifulSoup) -> None:
        token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
        token_addres = token_address_link.get("href").split("/")[-1]
        
        links = soup.find_all("a", class_="chakra-link chakra-button custom-1hhf88o")
        data = {}

        data["makers"] = [a.get("href").split("/")[-1] for a in links]
        
        sums = soup.find_all("div", class_="custom-1o79wax")
        bought_list = []
        sold_list = []
        for i in range(len(sums)):
            if sums[i].find("span").text == "-":
                number = None
            else:
                str_number = sums[i].find("span").text[1:]
                number = str_number.lstrip("0").lstrip("$")
                number = number.replace(",", "").replace(".", "").replace("K", "000").replace("M", "000000")
                number = int(number)
            
            if i % 2 == 0:
                bought_list.append(number)
            else:
                sold_list.append(number)
        data["bought"] = bought_list
        data["sold"] = sold_list

        token_address_link = soup.find_all("a", class_="chakra-link chakra-button custom-isf5h9")[1]
        token_addres = token_address_link.get("href").split("/")[-1]
        chain = "SOL"
        
        temp_df = pd.DataFrame(data)
        temp_df.dropna(inplace=True)
        temp_df["pnl"] = temp_df["sold"] - temp_df["bought"]
        
        for index, row in temp_df.iterrows():
            tt = TopTrader.objects.create(
                coin = "s",
                coin_address=token_addres,
                pair = pair,
                maker=row["makers"],
                chain=chain,
                bought=row["bought"],
                sold=row["sold"],
                PNL=row["pnl"]    
            )


    @sync_to_async
    def check_visited_link(pair: str):
        return list(TopTrader.objects.all().filter(pair=pair))
            

    async def rugcheck_coin(self, coin_address):
        rugcheck_page = await self.browser.get("https://rugcheck.xyz/tokens/" + coin_address, new_tab=True)
        await rugcheck_page
        time.sleep(10)
        risk_level = await rugcheck_page.query_selector("div.risk h1.mb-0")
        await rugcheck_page.close()
        
        return risk_level.text
         

    async def _get_2captcha_api_key(self):
        captcha_extenshion_page = await self.browser.get(settings.CAPTCHA_EXTENSION_LINK)
        api_key_input = await captcha_extenshion_page.select("input[name=apiKey]")
        
        await api_key_input.send_keys(settings.CAPTCHA_API_KEY)
        login_button = await captcha_extenshion_page.find("Login")
        await login_button.click()


    async def _check_cloudflare(self, page):
        await self.browser.wait(random.randint(1, 2))
        try:
            await page.find("Verifying you are human.")
            await self._bypass_cloudflare(page)
        except:
            return None


    async def _bypass_cloudflare(self, page):
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


async def run_dexscreener_watcher(filter):    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config)
    dex_worker = DexWorker(browser)
    await dex_worker.watch_coin(filter)


async def run_dexscreener_parser(filter, pages):    
    config = Config()
   # config.add_extension("./extensions/captcha_solver")
    browser = await uc.start(config=config, sandbox=False)
    dex_worker = DexWorker(browser)
    await dex_worker.parse_top_traders(filter, pages)
