import asyncio
import time
import logging
import pandas as pd
import random
from asgiref.sync import async_to_sync
from datetime import datetime
from django.conf import settings
from seleniumbase import SB
from bs4 import BeautifulSoup
from dexscreener import DexscreenerClient
import nodriver as uc
from nodriver.core.config import Config
from .parsers.sol_parser import SolscanParser
from .models import TopTrader
from .coin_checker import CoinChecker

logger = logging.getLogger(__name__)

class DexScreenerWorker():
    def __init__(self, browser, filter="?rankBy=trendingScoreH6&order=desc&minLiq=15000&maxAge=1"):
        self.filter = filter
        self.browser = browser
        
    async def watch_coin(self):
        #await self._get_2captcha_api_key()
        dex_page = await self.browser.get('https://dexscreener.com/solana' + self.filter)
        time.sleep(10)
        visited_links, black_list = [], []

        logger.info(f"Начат мониторинг DexScreener") 

        while True:
            all_links = await dex_page.query_selector_all("a.ds-dex-table-row")

            links = [item for item in all_links if item not in visited_links]
            await dex_page.wait(2)
            if links:
                for link in links:
                    await link.click()
                    await self.browser.wait(3)
                    visited_links.append(link)
                    
                    coin_link = await dex_page.select_all("a.custom-isf5h9")
                    coin_address = coin_link[1].attributes[-1].split("/")[-1]
                    await dex_page.wait(5)
                    risk_level = await self.rugcheck_coin(coin_address)

                    logger.info(f"Уровень риска монеты {coin_address}: {risk_level}")    
                    if risk_level != "Good":
                        black_list.append(link)
                        await dex_page.back()
                        await self.browser.wait(3)
                        
                        continue
                    
                    coin_checker = CoinChecker(coin_address)
                    
                    logger.info(f":) Анализ монеты {coin_address}")

                    await dex_page.back()
                    
                    await self.browser.wait(3)

            await self.browser.wait(10)
            
    async def rugcheck_coin(self, coin_address):
        rugcheck_page = await self.browser.get("https://rugcheck.xyz/tokens/" + coin_address, new_tab=True)
        await rugcheck_page.wait(2)
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
    dex_worker = DexScreenerWorker(browser, filter)
    await dex_worker.watch_coin()
    