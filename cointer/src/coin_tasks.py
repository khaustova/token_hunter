import logging
import time
from datetime import datetime
from core.celery import app
from .utils import get_coins_prices , get_coin_age
from ..models import Transaction, Status

logger = logging.getLogger(__name__)

STOP_LOSS = -20
TAKE_PROFIT = 60


@app.task
def track_coins() -> str:
    """
    Отслеживание стоимости купленных монет.
    Когда разница между текущей стоимостью и стоимостью покупки превышает 
    значение TAKE_PROFIT или ниже значения STOP_LOSS, происходит продажа монеты.
    """
    
    buying_prices = {}
    open_transactions = Transaction.objects.filter(status=Status.OPEN)
    for transaction in open_transactions:
        buying_prices[transaction.pair] = float(transaction.buying_price)

    while open_transactions:
        coins_str = ",".join(buying_prices.keys())
        coins_data = get_coins_prices(coins_str)
        
        for coin in coins_data:
            coin_address = coin["baseToken"]["address"]
            pair = coin["pairAddress"]
            buying_price = buying_prices[pair.lower()]
            current_price = float(coin["priceUsd"])
            pnl = ((current_price - buying_price) / buying_price) * 100
            
            if pnl >= 60 or pnl < -30:
                coin_age = get_coin_age(coin["pairCreatedAt"])
                
                Transaction.objects.filter(coin_address=coin_address).update(
                    selling_price=current_price,
                    selling_coin_age=coin_age,
                    selling_transactions_buys_m5=coin["txns"]["m5"]["buys"],
                    selling_transactions_sells_m5=coin["txns"]["m5"]["sells"],
                    selling_transactions_buys_h1=coin["txns"]["h1"]["buys"],
                    selling_transactions_sells_h1=coin["txns"]["h1"]["buys"],
                    selling_volume_m5=coin["volume"]["m5"],
                    selling_volume_h1=coin["volume"]["h1"],
                    selling_price_change_m5=coin["priceChange"]["m5"],
                    selling_price_change_h1=coin["priceChange"]["h1"],
                    selling_liquidity=coin["liquidity"]["usd"],
                    selling_fdv=coin["fdv"],
                    selling_market_cap=coin["marketCap"],
                    PNL=pnl,
                    status=Status.CLOSED
                    
                )
                logger.info(f"Продажа монеты {coin_address} за {current_price} USD") 
  
        time.sleep(1)
            
        open_transactions = Transaction.objects.filter(status=Status.OPEN)
        buying_prices = {}
        for transaction in open_transactions:
            buying_prices[transaction.pair] = float(transaction.buying_price)
    
    return "Обновление стоимости монет завершено"
