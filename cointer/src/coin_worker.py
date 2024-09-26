
import logging
import time
import httpx
import logging
from datetime import datetime
from httpx._config import Timeout
from .coin_tasks import track_coins
from .sol_parser import SolanaParser
from .utils import get_active_tasks, get_coins_prices, get_coin_age
from ..models import Status, Transaction

logger = logging.getLogger(__name__)


class CoinChecker:
    """
    Проверка монеты:
    - check_price_change - изменение цены за 5 минут, 1 час,
      6 часов и 24 часа (должно быть положительным);
    - check_txns - количество покупок за 5 минут, 1 час, 6 часов и 
      24 часа (должно быть больше количества продаж);
    - check_socio - наличие сайта, телеграма и твиттера;
    - check_boost - наличие буста на DexScreener.
    """
    
    def __init__(self, pair):
        self.pair = pair
        self.coin_data = get_coins_prices(self.pair)[0]
        self.coin_address = self.coin_data["baseToken"]["address"]
        self.coin_name = self.coin_data["baseToken"]["name"]
        
    def check_coin(self):
        if (#self.check_price_change() or
            #self.check_txns() or
            self.check_socio()
        ):
            return True
        
        return False
    
    def check_coin_age(self):
        coin_age = get_coin_age(self.coin_data["pairCreatedAt"])
        if coin_age > 5:
            return False
        
        return True
        
    def check_price_change(self):
        if self.coin_data["priceChange"]["m5"] < -10:
            logger.debug(f"⨉ Стоимость монеты {self.coin_name} падала больше, чем на 10 %")
            return False
            
        return True
    
    def check_txns(self):
        for txns in self.coin_data["txns"].values():
            if txns["buys"] < txns["sells"]:
                logger.debug(f"⨉ Количество покупок монеты {self.coin_name} меньше количества продаж")  
                return False
             
        return True
    
    def check_socio(self):
        info = self.coin_data.get("info", None)
        if not info:
            logger.debug(f"⨉ У монеты {self.coin_name} нет сайта или социальных сетей") 
            return False
            # if not info.get("websites", None) and not info.get("socials", None):
            #     logger.debug(f"⨉ У монеты {self.coin_name} нет сайта и социальных сетей") 
            #     return False

        return True
    
    def check_boost(self):
        if self.coin_data["boosts"]:
            return True
        
        return False
    
    def check_total_transfers(self, total_transfers):
        total_transactions = self.coin_data["txns"]["h1"]["buys"] + self.coin_data["txns"]["h1"]["sells"]
        if total_transfers is None or total_transfers > 5000:
            logger.debug(f"⨉ Количество трансферов монеты {self.coin_name} сильно превышает количество транзакций") 
            return False
        
        return True
    
    def check_token(self):
        tokens_url = f"https://api.dexscreener.com/latest/dex/tokens/{self.coin_address}"
        num_tokens = None
        while not num_tokens:
            time.sleep(1)
            try:
                num_tokens = httpx.get(tokens_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
            except:
                continue
            
        if len(num_tokens) != 1:
            logger.debug(f"⨉ На бирже обнаружены другие монеты {self.coin_name} с адрессом {self.coin_address}") 
            return False
        
        return True
    
    def save_transactions_history(self):
        solana_parser = SolanaParser()
        solana_parser.get_transactions_history(self.coin_name, self.coin_address)


def buy_coin(pair, total_transfers, coin_name, coin_address):
    """
    Покупка монеты.
    """
    telegram, twitter, website = False, False, False
    coin_data = get_coins_prices(pair)[0]
    socio_info = coin_data.get("info")
    
    # coin_checker = CoinChecker(pair)
    # coin_checker.save_transactions_history()
    
    if socio_info:
        if socio_info.get("websites"):
            website = True
        if socio_info.get("socials"):
            for socio in socio_info.get("socials"):
                if socio.get("type") == "twitter":
                    twitter = True
                elif socio.get("type") == "telegram":
                    telegram = True
                    
    coin_age = get_coin_age(coin_data["pairCreatedAt"])

    Transaction.objects.get_or_create(
        pair=pair,
        coin=coin_name,
        coin_address=coin_address,
        buying_coin_age=coin_age,
        buying_price=coin_data["priceUsd"],
        buying_transactions_buys_m5=coin_data["txns"]["m5"]["buys"],
        buying_transactions_sells_m5=coin_data["txns"]["m5"]["sells"],
        buying_transactions_buys_h1=coin_data["txns"]["h1"]["buys"],
        buying_transactions_sells_h1=coin_data["txns"]["h1"]["buys"],
        buying_total_transfers = total_transfers,
        buying_total_transactions = coin_data["txns"]["h1"]["buys"] + coin_data["txns"]["h1"]["buys"],
        buying_volume_m5=coin_data["volume"]["m5"],
        buying_volume_h1=coin_data["volume"]["h1"],
        buying_price_change_m5=coin_data["priceChange"]["m5"],
        buying_price_change_h1=coin_data["priceChange"]["h1"],
        buying_liquidity=coin_data["liquidity"]["usd"],
        buying_fdv=coin_data["fdv"],
        buying_market_cap=coin_data["marketCap"],
        is_telegram=telegram,
        is_twitter=twitter,
        is_website=website,
        status=Status.OPEN,
    )

    logger.info(f"Покупка монеты {coin_name} за {coin_data["priceUsd"]} USD") 
    is_update_process = False
    try:
        active_tasks = get_active_tasks()
        for task in active_tasks:
            if task["name"] == "cointer.src.coin_tasks.track_coins":
                is_update_process = True
                break
    except:   
        is_update_process = False
        
    if not is_update_process:
        track_coins.delay()
