import logging
import json
import time
import os
import pandas as pd
import undetected_chromedriver as uc
from datetime import datetime
from helius import TransactionsAPI
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin

SOLANA_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

logger = logging.getLogger(__name__)


class SolanaParser():
    """
    Позволяет получать информацию о транзакциях в сети Solana.
    с использованием Helius API. 
    """
    
    def __init__(self):
        self._transactions_api = TransactionsAPI(HELIUS_API_KEY)
        
    def get_transactions_history(self, name: str, address: str, number: int=100):
        last_transaction = ""
            
        logger.info(f"Начата загрузка истории транзакций для токена {address}.")  
          
        transaction_history = []
        while True:
            # Загрузка истории транзакций длится до тех пор, пока не будет 
            # найдена последняя транзакция.
            transactions = self._transactions_api.get_parsed_transaction_history(
                address=address, 
                before=last_transaction
            )
            if not transactions:
                transaction_history.reverse()
                logger.info(f"История транзакций токена {address} успешно загружена.")
                break
            
            last_transaction = transactions[-1]["signature"]
            transaction_history.extend(transactions)
            
        if number < len(transaction_history):
            transaction_history = transaction_history[:number]
        
        os.makedirs(f"/transactions_history/{name}", exist_ok=True)
        
        step = 1
        for transaction in transaction_history:
            with open(f"/transactions_history/{name}/{name}_{step}.json", "w") as file:
                json.dump(transaction, file)
            step += 1
        
        return 
    
    def _get_transaction_info(self, transaction, address):
        """
        Вовзращает информацию о транзакции, если она относится к покупке, 
        запрашиваемой через Helius API.
        """
        
        transaction_info = {}
        try:
            transaction_info["who"] = transaction["feePayer"]
            transaction_info["signature"] = transaction["signature"]

            if ( # Если просходит покупка:
                transaction["tokenTransfers"][0]["mint"] == SOLANA_TOKEN_ADDRESS 
                and transaction["tokenTransfers"][1]["mint"] == address
            ):
                transaction_info["type"] = "buy"
                transaction_info["sol"] = transaction["tokenTransfers"][0]["tokenAmount"]
                transaction_info["token"] = transaction["tokenTransfers"][1]["tokenAmount"] 
                
            elif ( # Если происходит продажа:
                transaction["tokenTransfers"][1]["mint"] == SOLANA_TOKEN_ADDRESS 
                and transaction["tokenTransfers"][0]["mint"] == address
            ):
                transaction_info["type"] = "sell"
                transaction_info["sol"] = transaction["tokenTransfers"][1]["tokenAmount"]
                transaction_info["token"] = transaction["tokenTransfers"][0]["tokenAmount"] 
        except:
            return None
        
        return transaction_info


class SolscanParser:
    """
    Парсит данные с https://solscan.io/.
    """
    
    def __init__(self, address: str):
        self.url = "https://solscan.io/account/"
        self.driver = None
        self.address = address

    def __enter__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--headless")

        self.driver = uc.Chrome(use_subprocess=True, options=chrome_options)
        self.prepare_parsing()
        
        return self

    def __exit__(self, exc_type, exc_value, _):
        if exc_type:
            logger.error(f"При закрытии браузера произошла ошибка: {exc_value}")

        if self.driver:
            self.driver.close()

        return False
    
    def prepare_parsing(self):
        url = urljoin(self.url, self.address)

        driver = self.driver
        driver.get(url)

        driver.execute_script(f"window.open('{url}', '_blank')")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        driver.close()
        
        driver.switch_to.window(driver.window_handles[0])
        
        return driver
        
    def get_balance(self):       
        try:
            print(self.driver.title)
            # logger.info(f"Начата загрузка баланса токенов на аккаунте {self.address}")
            
            # balance_button = driver.find_element(By.XPATH, '//button[text()="Portfolio"]')
            # balance_button.click()
            # print(balance_button.text)
        
            # element = WebDriverWait(driver, 5).until(
            #     EC.presence_of_element_located(
            #         (
            #             By.XPATH,
            #             (
            #                 "//table/tbody/tr[2]/td[1]/span/span[1]/a"
            #             ),
            #         )
            #     )
            # )
            # return element.text
            
        except TimeoutException:
            logger.info(f"На странице не найдена информация по балансу на аккаунте {self.address}")
            pass

        return None