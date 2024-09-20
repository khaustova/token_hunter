import logging
import time
import pgbulk
from celery.contrib.abortable import AbortableTask
from core.celery import app
from .utils import get_coins_prices 
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
            if coin["dexId"] == "raydium":
                coin_address = coin["baseToken"]["address"]
                pair = coin["pairAddress"]
                buying_price = buying_prices[pair.lower()]
                current_price = float(coin["priceUsd"])
                pnl = ((current_price - buying_price) / buying_price) * 100
                if pnl > TAKE_PROFIT or pnl < STOP_LOSS:
                    Transaction.objects.filter(coin_address=coin_address).update(
                        selling_price=current_price,
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
