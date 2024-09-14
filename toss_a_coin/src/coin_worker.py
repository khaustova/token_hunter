
import logging
import httpx
import time
from httpx._config import Timeout
from .coin_tasks import update_current_prices, track_coin
from .utils import get_active_tasks, get_coins_prices
from ..models import Transaction, Status

logger = logging.getLogger(__name__)


class CoinChecker:
    
    def __init__(self, pair):
        self.pair = pair
        self.coin_data = self.get_coin_data()
        self.coin_address = self.coin_data["baseToken"]["address"]
        self.coin_name = self.coin_data["baseToken"]["name"]
        
        
    def get_coin_data(self) -> dict:
        coin_data_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{self.pair}"
        coin_data = httpx.get(coin_data_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
        print(coin_data)
        if coin_data:
            return coin_data[0]
        
        time.sleep(1)
        self.get_coin_data()
        
        
    def check_coin(self):
        if (self.check_price_change() and
            self.check_txns() and
            self.check_socio()
        ):
            return True
        
        return False
        
        
    def check_price_change(self):
        for price_change in self.coin_data["priceChange"].values():
            if price_change < 0 or price_change == 0:
                logger.debug(f"Стоимость монеты {self.coin_name} падала на рассматриваемом промежутке времени")
                return False
            
        logger.debug(f"Стоимость монеты {self.coin_name} растёт на всём промежутке времени")  
        return True


    def check_txns(self):
        for txns in self.coin_data["txns"].values():
            if txns["buys"] < txns["sells"]:
                logger.debug(f"Количество покупок монеты {self.coin_name} меньше количества продаж")  
                return False
            
        logger.debug(f"Количество покупок монеты {self.coin_name} больше количества продаж")  
        return True


    def check_socio(self):
        info = self.coin_data.get("info", None)
        if info:
            if info["websites"] and info["socials"]:
                logger.debug(f"У монеты {self.coin_name} есть сайт и социальные сети") 
                return True
            
        logger.debug(f"У монеты {self.coin_name} нет сайта и социальных сетей") 
        return False


    def check_boost(self):
        if self.coin_data["boosts"]:
            return True
        
        return False


def buy_coin(coin_name, coin_address):
    coin_price = get_coins_prices(coin_address)[0]["priceUsd"]
    Transaction.objects.get_or_create(
        coin=coin_name,
        coin_address=coin_address,
        buying_price=coin_price,
        current_price=coin_price,
        status=Status.OPEN,
    )
    
    is_update_process = False
    try:
        active_tasks = get_active_tasks()
        for task in active_tasks:
            if task["name"] == "toss_a_coin.src.coin_tasks.update_current_prices":
                is_update_process = True
                break
    except:   
        is_update_process = False
        
    if not is_update_process:
        update_current_prices.delay()
        
    track_coin.delay(coin_address)




    

