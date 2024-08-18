import time
import os
import undetected_chromedriver as uc
from datetime import datetime
from helius import TransactionsAPI
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from solana.rpc.api import Client
from solders.signature import Signature
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp
from urllib.parse import urljoin
from logger import get_logger

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com/" 
SOLANA_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

logger = get_logger(__name__)

class SolanaParser():
    """
    Позволяет получать информацию о транзакциях в сети Solana.
    Поддерживает работу с Helius API и открытой RPC-точкой Mainnet Beta
    в зависимости от параметра mode. 
    """
    
    def __init__(self, mode="Helius"):
        self._open_client = Client(SOLANA_RPC_URL, timeout=50)
        self._transactions_api = TransactionsAPI(HELIUS_API_KEY)
        self.mode = mode
        
    def get_first_buy_transactions(self, number: int, address: str):
        """
        Возвращает запрашиваемое количество первых покупок токена за Sol.
        """
        
        last_transaction = ""
        if not self.mode == "Helius":
            token_address = Pubkey.from_string(address)
            last_transaction = None
            
        logger.info(f"Начата загрузка истории транзакций для токена {address}.")  
          
        transaction_history, prev_transaction_history = [], []
        while True:
            # Загрузка истории транзакций длится до тех пор, пока не будет 
            # найдена последняя транзакция.
            if self.mode == "Helius":
                
                transactions = self._transactions_api.get_parsed_transaction_history(
                    address=address, 
                    before=last_transaction
                )
            else:  
                signatures_response = self._open_client.get_signatures_for_address(
                    token_address, 
                    before=last_transaction, 
                    limit=1000
                )
                transactions = [t.signature for t in signatures_response.value] 
                time.sleep(5) # задержка для избежания ошибки 429
                
            if not transactions:
                if prev_transaction_history:
                    prev_transaction_history.extend(transaction_history)
                    transaction_history = prev_transaction_history
                transaction_history.reverse()
                logger.info(f"История транзакций токена {address} успешно загружена. Адрес последней транзакции: {last_transaction}.")
                break
            
            last_transaction = transactions[-1]["signature"] if self.mode == "Helius" else transactions[-1]
                
            prev_transaction_history = transaction_history
            transaction_history = transactions
            
        if number > len(transaction_history):
            number = len(transaction_history)
                
        first_buy_transactions = [] 
        
        logger.info(f"Начато получение информации о первых {number} покупках токена {address}.")  
        current_number = 1 
        for transaction in transaction_history:
            # Транзакции фильтруются и учитываются лишь относящиеся к покупке.
            if current_number <= number:
                if self.mode == "Helius":
                    transaction_info = self.get_helius_transaction_info(transaction, address)
                else:
                    transaction_info = self.get_open_transaction_info(transaction)
                    
                if transaction_info:
                    logger.debug(f"Транзакция {current_number}: {transaction_info}")
                    first_buy_transactions.append(transaction_info)
                    current_number += 1
                
        
        logger.info(f"Получена информация о первых {current_number} покупках токена {address}.") 
                    
        return first_buy_transactions
    
    def get_helius_transaction_info(self, transaction, address):
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
                
            
    def get_open_transaction_info(self, signature: Signature):
        """
        Вовзращает информацию о транзакции, если она относится к покупке, 
        запрашиваемой через Mainnet Beta.
        """   
        
        transaction = self._open_client.get_transaction(signature, encoding="jsonParsed", max_supported_transaction_version=0)
        
        time.sleep(5) # Задержка для избежания ошибки 429.
        
        transaction_info = {}
        transaction_info["who"] = str(transaction.value.transaction.transaction.message.account_keys[0].pubkey)
        transaction_info["signature"] = str(signature)
        transaction_info["type"] = self.get_open_transaction_type(transaction)
        
        if not transaction_info["type"]:
            return None
        
        if transaction.value.transaction.meta.err != None:
            return None
        
        for ui_instruction in transaction.value.transaction.meta.inner_instructions:
            for instruction in ui_instruction.instructions:
                try:
                    if instruction.parsed.get("type") == "transfer":
                        amount = instruction.parsed.get("info").get("amount")
                        if amount:
                            authority = instruction.parsed.get("info").get("authority")
                            if transaction_info["type"] == "buy":
                                if authority == transaction_info["who"]: 
                                    transaction_info["sol"] = amount
                                else:
                                    transaction_info["coin"] = amount
                            elif transaction_info["type"] == "sell":
                                if authority == transaction_info["who"]: 
                                    transaction_info["coin"] = amount
                                else:
                                    transaction_info["sol"] = amount                                
                                
                                
                except:
                    continue 
        
        return transaction_info

    @staticmethod
    def get_open_transaction_type(transaction: GetTransactionResp):
        """
        Определяет является ли покупкой транзакция, запрашиваемая через Mainnet Beta.
        """
        
        pre_sol_balance, post_sol_balance = None, None
        for token in transaction.value.transaction.meta.pre_token_balances:
            if str(token.mint) == SOLANA_TOKEN_ADDRESS:
                pre_sol_balance = token.ui_token_amount.amount
                break
                
        for token in transaction.value.transaction.meta.post_token_balances:
            if str(token.mint) == SOLANA_TOKEN_ADDRESS:
                post_sol_balance = token.ui_token_amount.amount
                break
        
        if pre_sol_balance and post_sol_balance: 
            if int(pre_sol_balance) - int(post_sol_balance) < 0:
                return "buy"
            elif int(pre_sol_balance) - int(post_sol_balance) > 0:
                return "sell"
            
        return False


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