import logging
import time
from celery.contrib.abortable import AbortableTask
from core.celery import app
from .utils import get_coins_prices 
from ..models import Transaction, Status

logger = logging.getLogger(__name__)

@app.task(bind=True, base=AbortableTask)
def update_current_prices() -> str:
    coins_list = list(Transaction.objects.filter(status=Status.OPEN))
    while coins_list:
        coin_prices = get_coins_prices(",".join(coins_list))
        for coin in coin_prices:
            Transaction.objects.filter(
                coin_address=coin["baseToken"]["address"]
            ).update(
                current_price=coin["priceUsd"]
            )

        time.sleep(1)
        
        coins_list = list(Transaction.objects.filter(status=Status.OPEN))
    
    return "Обновление стоимости монет завершено"


@app.task(bind=True, base=AbortableTask)
def track_coin(coin_address: str) -> str:
    while True:
        transaction = Transaction.objects.get(coin_address=coin_address)
        buying_price = transaction.buying_price
        current_price = transaction.current_price
        pnl = ((current_price - buying_price) / buying_price) * 100
        
        if pnl > 50 or pnl < -50:
            Transaction.objects.filter(coin_address=coin_address).update(
                selling_price=current_price,
                status=Status.CLOSED
        )
            break
        else:
            time.sleep(1)
            
    return "Продано"