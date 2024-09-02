import time
import logging
import pandas as pd
import random
from datetime import datetime
from django.conf import settings
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
        self._get_2captcha_api_key()
        self.sb.uc_open_with_reconnect("https://dexscreener.com/solana/page-" + pages + filter, reconnect_time=4)
        #self.sb.uc_gui_click_captcha() 
        self._check_cloudflare()

        visited_links = set()
        black_list = set()

        logger.info(f"Начат мониторинг DexScreener")  
        while True:
            links = set(self.sb.find_elements("xpath", "//a[contains(@class, 'ds-dex-table-row')]"))
            self.sb.sleep(random.randint(1, 3))
            links -= visited_links

            if links:
                for link in links:
                    self._check_cloudflare()
                    
                    try:
                        if link in visited_links or link in black_list:
                            continue
                        else:
                            link.click()
                            self._check_cloudflare()      
                            visited_links.add(link)
                    except Exception as e:
                        logger.error(f"Не удалось перейти по ссылке")
                        continue

                    self.sb.sleep(random.randint(2, 3))

                    coin_link = self.sb.find_elements("xpath", "//a[contains(@class, 'custom-isf5h9')]")[1]
                    coin_address = coin_link.get_attribute("href").split("/")[-1]
                    
                    coin_checker = CoinChecker(coin_address)
                    
                    risk_level = coin_checker.rugcheck_coin()
                    if risk_level != "Good":
                        logger.info(f"Монета на {link.get_attribute("href")} не прошла проверку на rugcheck.xyz, уровень риска: {risk_level}") 
                        black_list.add(link)
                        self.sb.go_back()
                        time.sleep(random.randint(2, 3))
                        continue
                    logger.info(f"Монета на {link.get_attribute("href")} прошла проверку на rugcheck.xyz, уровень риска: {risk_level}")    
                    
                    logger.info(f":) Анализ монеты {link.get_attribute("href")}")
                    
                    self.sb.go_back()
                    time.sleep(random.randint(2, 3))
                    
    def _get_2captcha_api_key(self):
        self.sb.uc_open_with_reconnect(settings.CAPTCHA_EXTENSION_LINK)
        time.sleep(1)
        input_element = self.sb.find_element("xpath", "//input[@name='apiKey']")
        input_value = input_element.get_attribute("value")
        
        if not input_value:
            input_element.send_keys(settings.CAPTCHA_API_KEY)

        self.sb.find_element("xpath", "//button[@id='connect']").click()
        self.sb.wait_for_and_accept_alert()
        
    def _bypass_cloudflare(self):
        self.sb.refresh()
        time.sleep(5)
    
        try:
            self.sb.find_element("div.captcha-solver-info").click()
        except:
            logger.debug("Кнопка 2Captcha не найдена, повтор попытки")
            self.sb.refresh()
            self._bypass_cloudflare()
            
        while "Один момент" in self.sb.get_title() or "Just a moment" in self.sb.get_title():
            logger.debug("Ожидание ответа от 2captcha...")
            time.sleep(5)
            
        logger.info("Защита Cloudflare успешно пройдена")
            
    def _check_cloudflare(self):
        self.sb.sleep(random.randint(1, 2))
        if "Один момент" in self.sb.get_title() or "Just a moment" in self.sb.get_title():
            logger.debug("Обнаружена защита Cloudflare")
            self._bypass_cloudflare()
              
    def get_last_transactions(self):
        rows = len(self.sb.find_elements("xpath", "//table/tbody/tr"))
        element = self.sb.find_element("xpath", "//table/tbody/tr[3]")
    