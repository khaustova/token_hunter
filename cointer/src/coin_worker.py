
import logging
from .coin_tasks import track_coins
from .utils import get_active_tasks, get_coins_prices
from ..models import Transaction, Status

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
         
    # def get_coin_data(self) -> dict:
    #     coin_data_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{self.pair}"
    #     coin_data = httpx.get(coin_data_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
    #     while not coin_data:
    #         time.sleep(1)
    #         coin_data = httpx.get(coin_data_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
        
    #     return coin_data[0]
        
    def check_coin(self):
        if (self.check_price_change() or
            self.check_txns() or
            self.check_socio()
        ):
            return True
        
        return False
        
    def check_price_change(self):
        for price_change in self.coin_data["priceChange"].values():
            if price_change < 0 or price_change == 0:
                logger.debug(f"⨉ Стоимость монеты {self.coin_name} падала на рассматриваемом промежутке времени")
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
        if info:
            if not info["websites"] and info["socials"]:
                logger.debug(f"⨉ У монеты {self.coin_name} нет сайта и социальных сетей") 
                return False

        return True
    
    def check_boost(self):
        if self.coin_data["boosts"]:
            return True
        
        return False


def buy_coin(pair, coin_name, coin_address):
    """
    Покупка монеты.
    """
    
    coin_price = get_coins_prices(pair)[0]["priceUsd"]
    Transaction.objects.get_or_create(
        pair=pair,
        coin=coin_name,
        coin_address=coin_address,
        buying_price=coin_price,
        current_price=coin_price,
        status=Status.OPEN,
    )
    logger.info(f"Покупка монеты {coin_name} за {coin_price} USD") 
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
