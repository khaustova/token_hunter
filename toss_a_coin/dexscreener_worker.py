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
from .check_coin import CoinChecker

logger = logging.getLogger(__name__)


class DexScreeneWatcher():
    
    def __init__(self, sb: SB):
        self.sb = sb

    def watch_coins(self, pages: str, filter: str=""):
        if not filter:
            filter = "?rankBy=trendingScoreH6&order=desc&minLiq=5000&maxAge=1"
        
        self.sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + pages + filter, reconnect_time=4)
        self.sb.uc_gui_handle_cf()
        self.sb.sleep(random.randint(6, 7))
        
        if self.sb.get_title() == "Just a moment...":
            logger.error("Не удалось победить Cloudflare")
            raise Exception("Cloudflare! :(")
        
        visited_links = set()
        bad_links = set()
        coin_checker = CoinChecker()
        logger.info(f"Начат мониторинг DexScreener")  
        while True:
   
            links = set(self.sb.find_elements("//a[contains(@class, 'ds-dex-table-row')]", by="xpath"))
            self.sb.sleep(random.randint(5, 10))
            links -= visited_links

            if links:
                for link in links:
                    try:
                        link_href = link.get_attribute("href")
                        pair = link_href.split("/")[-1]
                        if link in visited_links:
                            logger.debug(f"Монета {link.get_attribute("href")} уже посещалась")
                            continue
                        else:
                            link.click()
                            visited_links.add(link)
                    except Exception as e:
                        logger.error(f"Не удалось прочитать адрес ссылки")
                        continue

                    self.sb.sleep(random.randint(2, 3))
                    
                    try:
                        self.sb.find_element("//span[text()='No issues']", by="xpath")
                    except Exception as e:
                        logger.info(f"Монета на странице {link.get_attribute("href")} небезопасна")
                        bad_links.add(pair)
                        self.sb.go_back()
                        time.sleep(random.randint(2, 3))
                        continue
                        
                    logger.info(f"Анализ монеты {link.get_attribute("href")}")
                    
                    self.sb.go_back()
                    time.sleep(random.randint(2, 3))
