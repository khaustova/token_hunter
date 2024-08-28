import time
import logging
import pandas as pd
import random
from datetime import datetime
from seleniumbase import SB
from bs4 import BeautifulSoup
from dexscreener import DexscreenerClient
from .parsers.sol_parser import SolscanParser
from .models import TopTrader
from .coin_checker import CoinChecker

logger = logging.getLogger(__name__)


class DexScreeneWatcher():
    
    def __init__(self, sb: SB):
        self.sb = sb

    def watch_coins(self, pages: str, filter: str=""):
        if not filter:
            filter = "?rankBy=trendingScoreH6&order=desc&minLiq=5000&maxAge=1"
        
        self.sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + pages + filter, reconnect_time=4)
        self.sb.uc_gui_click_captcha() 
        self.sb.sleep(random.randint(6, 7))
        
        # if self.sb.get_title() == "Just a moment...":
        #     logger.error("Не удалось победить Cloudflare")
        #     raise Exception("Cloudflare! :(")
        
        visited_links = set()
        black_list = set()

        logger.info(f"Начат мониторинг DexScreener")  
        while True:
   
            links = set(self.sb.find_elements("//a[contains(@class, 'ds-dex-table-row')]", by="xpath"))
            self.sb.sleep(random.randint(5, 10))
            links -= visited_links
            

            if links:
                for link in links:
                    try:
                        
                        if link in visited_links or link in black_list:
                            continue
                        else:
                            link.uc_click()
                            visited_links.add(link)
                    except Exception as e:
                        logger.error(f"Не удалось прочитать адрес ссылки: {e}")
                        continue

                    self.sb.sleep(random.randint(2, 3))

                    try:
                        self.sb.find_element("//span[text()='No issues']", by="xpath")
                    except Exception as e:
                        logger.info(f"Монета на странице {link.get_attribute("href")} небезопасна")
                        black_list.add(link)
                        self.sb.go_back()
                        time.sleep(random.randint(2, 3))
                        continue
                    
                    
                    coin_link = self.sb.find_elements("//a[contains(@class, 'custom-isf5h9')]", by="xpath")[1]
                    coin_address = coin_link.get_attribute("href").split("/")[-1]
                    
                    coin_checker = CoinChecker(coin_address)
        
                    first_checking_coin = coin_checker.first_check_coin()
                    if not first_checking_coin:
                        logger.info(f"Монета на странице {link.get_attribute("href")} не прошла проверку на rugcheck.xyz")
                        black_list.add(link)
                        self.sb.go_back()
                        time.sleep(random.randint(2, 3))
                        continue
                        
                    logger.info(f"Анализ монеты {link.get_attribute("href")}")
                    
                    self.sb.go_back()
                    time.sleep(random.randint(2, 3))
                    
    def get_last_transactions(self):
        rows = len(self.sb.find_elements("xpath", "//table/tbody/tr"))
        print(rows)
        self.sb.scroll_to("//table/tbody/tr", "bottom")
        rows = len(self.sb.find_elements("xpath", "//table/tbody/tr"))
        print(rows)
        element = self.sb.find_element("xpath", "//table/tbody/tr[3]")
        print(element.text)
        
    def bypass_cloudflare(self):
        self.sb.get('chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html')
        time.sleep(1)
        self.sb.find_element("xpath", "//input[@name='apiKey']").send_key("key")
        self.sb.find_element("xpath", "//button[@id='connect']").click()
        self.sb.wait_for_and_accept_alert()
        
        self.sb.get('https://dexscreener.com/')
        time.sleep(4)
        self.sb.find_element("css_selector", ".captcha-solver-info").click()
