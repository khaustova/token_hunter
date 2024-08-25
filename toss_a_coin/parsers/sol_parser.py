import logging
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
from logger import get_logger

SOLANA_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

logger = logging.getLogger(__name__)


class SolanaParser():
    """
    Позволяет получать информацию о транзакциях в сети Solana .
    с использованием Helius API. 
    """
    
    def __init__(self):
        self._transactions_api = TransactionsAPI(HELIUS_API_KEY)
        
    def get_transactions_history(self, address: str, number: None=None):
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
            
            last_transaction = transactions[-1]["signature"] if self.mode == "Helius" else transactions[-1]
            transaction_history.extend(transactions)
            
        if number and number < len(transaction_history):
                transaction_history = transaction_history[:number]
        else:
            number = len(transaction_history)
        transaction_history.append(1)         
        info_for_each_transactions = [] 
        
        logger.info(f"Начато получение информации о первых {number} покупках токена {address}.")  
        current_number = 1 
        for transaction in transaction_history:
            # Транзакции фильтруются и учитываются лишь относящиеся к покупке.
            if current_number <= number:
                transaction_info = self._get_transaction_info(transaction, address)
                    
                if transaction_info:
                    logger.debug(f"Транзакция {current_number}: {transaction_info}")
                    info_for_each_transactions.append(transaction_info)
                    current_number += 1      
        
        logger.info(f"Получена информация о первых {current_number} покупках токена {address}.")
        
        temp_df = pd.DataFrame(info_for_each_transactions)
        temp_df.to_csv('history.csv')
        
        return info_for_each_transactions
    
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
                transaction_info["coin"] = transaction["tokenTransfers"][1]["tokenAmount"] 
                
            elif ( # Если происходит продажа:
                transaction["tokenTransfers"][1]["mint"] == SOLANA_TOKEN_ADDRESS 
                and transaction["tokenTransfers"][0]["mint"] == address
            ):
                transaction_info["type"] = "sell"
                transaction_info["sol"] = transaction["tokenTransfers"][1]["tokenAmount"]
                transaction_info["coin"] = transaction["tokenTransfers"][0]["tokenAmount"] 
        except:
            return None
        
        return transaction_info


class SolscanParser:
    """
    Парсит данные с https://solscan.io/.
    """
    
    def __init__(self):
        self.url = "https://solscan.io/account/"
        self.driver = None

    def __enter__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--headless")

        self.driver = uc.Chrome(use_subprocess=True, options=chrome_options)

        return self

    def __exit__(self, exc_type, exc_value, _):
        if exc_type:
            logger.error(f"При закрытии браузера произошла ошибка: {exc_value}")

        if self.driver:
            self.driver.close()

        return False
    
    def prepare_parsing(self, address: str):
        url = urljoin(self.url, address)

        driver = self.driver
        driver.get(url)

        driver.execute_script(f"window.open('{url}', '_blank')")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        driver.close()
        
        driver.switch_to.window(driver.window_handles[0])
        
        return driver
        
    def get_balance(self, address: str):       
        driver = self.prepare_parsing(address)

        try:
            print(driver.title)
            logger.info(f"Начата загрузка баланса токенов на аккаунте {address}")
            
            balance_button = driver.find_element(By.XPATH, '//button[text()="Portfolio"]')
            balance_button.click()
            print(balance_button.text)
        
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        (
                            "//table/tbody/tr[2]/td[1]/span/span[1]/a"
                        ),
                    )
                )
            )
            return element.text
            
        except TimeoutException:
            logger.info(f"На странице не найдена информация по балансу на аккаунте {address}")
            pass

        return None