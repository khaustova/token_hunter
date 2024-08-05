import time
import asyncio
from solana.rpc.api import Client
from typing import Optional
from helius import TransactionsAPI
from solders.signature import Signature
from solders.pubkey import Pubkey
from solders.rpc.responses import GetTransactionResp
from configuration import configuration
from logger.logger import get_logger

SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com/" 
SOLANA_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"

logger = get_logger(__name__)

class SolanaParser():
    """
    Позволяет получать информацию о транзакциях в сети Solana.
    Поддерживает работу с Helius API и открытой RPC-точкой Mainnet Beta
    в зависимости от параметра mode. 
    """
    
    def __init__(self, mode="Helius"):
        self.open_client = Client(SOLANA_RPC_URL, timeout=50)
        self.helius_client = TransactionsAPI(configuration.solana.api_key)
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
                
                transactions = self.helius_client.get_parsed_transaction_history(
                    address=address, 
                    before=last_transaction
                )
            else:  
                signatures_response = self.open_client.get_signatures_for_address(
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
        current_number = 0 
        for transaction in transaction_history:
            # Транзакции фильтруются и учитываются лишь относящиеся к покупке.
            if current_number < number:
                if self.mode == "Helius":
                    transaction_info = self.__get_helius_transaction_info(transaction, address)
                else:
                    transaction_info = self.__get_open_transaction_info(transaction)
                    
                if transaction_info:
                    first_buy_transactions.append(transaction_info)
                    current_number += 1  
        
        logger.info(f"Получена информация о первых {current_number} покупках токена {address}.") 
                    
        return first_buy_transactions
    
    def __get_helius_transaction_info(self, transaction, address):
        """
        Вовзращает информацию о транзакции, если она относится к покупке, 
        запрашиваемой через Helius API.
        """
        
        transaction_info = {}
        try:
            if transaction["tokenTransfers"][0]["mint"] == SOLANA_TOKEN_ADDRESS and transaction["tokenTransfers"][1]["mint"] == address:
                transaction_info["who"] = transaction["feePayer"]
                transaction_info["signature"] = transaction["signature"]
                transaction_info["sol"] = transaction["tokenTransfers"][0]["tokenAmount"]
                transaction_info["coin"] = transaction["tokenTransfers"][1]["tokenAmount"] 
        except:
            return None
        
        return transaction_info
                
            
    def __get_open_transaction_info(self, signature: Signature):
        """
        Вовзращает информацию о транзакции, если она относится к покупке, 
        запрашиваемой через Mainnet Beta.
        """   
        
        transaction = self.open_client.get_transaction(signature, encoding="jsonParsed", max_supported_transaction_version=0)
        
        time.sleep(5) # задержка для избежания ошибки 429
        
        transaction_info = {}
        transaction_info["who"] = str(transaction.value.transaction.transaction.message.account_keys[0].pubkey)
        transaction_info["signature"] = str(signature)
        transaction_info["type"] = self.__filter_open_transaction_type(transaction)
        
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
                            if authority == transaction_info["who"]: 
                                transaction_info["sol"] = amount
                            else:
                                transaction_info["coin"] = amount
                except:
                    continue 
        
        return transaction_info

    @staticmethod
    def __filter_open_transaction_type(transaction: GetTransactionResp):
        """
        Определяет тип транзакции, запрашиваемой через Mainnet Beta.
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
        
        if (
            pre_sol_balance 
            and post_sol_balance 
            and int(pre_sol_balance) - int(post_sol_balance) <= 0
        ):
            return "buy"
            
        return None
