import logging
import time
from datetime import datetime
from core.celery import app
from ..utils import get_token_data, get_token_age
from ...models import Transaction, Status, Settings
from django.utils import timezone

logger = logging.getLogger(__name__)

try:
    settings = Settings.objects.all().first()
    STOP_LOSS = settings.stop_loss
    TAKE_PROFIT = settings.take_profit
except:
    STOP_LOSS = -20
    TAKE_PROFIT = 60


@app.task
def track_tokens() -> str:
    """
    Отслеживает стоимость купленных токенов.
    Когда разница между текущей стоимостью и стоимостью покупки превышает 
    значение TAKE_PROFIT или ниже значения STOP_LOSS, происходит продажа токена.
    """
    
    buying_prices = {}
    open_transactions = Transaction.objects.filter(status=Status.OPEN)
    for transaction in open_transactions:
        buying_prices[transaction.pair] = float(transaction.buying_price)

    while open_transactions:
        tokens_str = ",".join(buying_prices.keys())
        tokens_data = get_token_data(tokens_str)
        
        for token_data in tokens_data:
            token_address = token_data["baseToken"]["address"]
            pair = token_data["pairAddress"]
            buying_price = buying_prices[pair.lower()]
            current_price = float(token_data["priceUsd"])
            pnl = ((current_price - buying_price) / buying_price) * 100
            
            if pnl >= TAKE_PROFIT or pnl <= STOP_LOSS:
                token_age = get_token_age(token_data["pairCreatedAt"])
                
                Transaction.objects.filter(token_address=token_address).update(
                    selling_price=current_price,
                    selling_token_age=token_age,
                    selling_buys_m5=token_data["txns"]["m5"]["buys"],
                    selling_sells_m5=token_data["txns"]["m5"]["sells"],
                    selling_buys_h1=token_data["txns"]["h1"]["buys"],
                    selling_sells_h1=token_data["txns"]["h1"]["sells"],
                    selling_buys_h6=token_data["txns"]["h6"]["buys"],
                    selling_sells_h6=token_data["txns"]["h6"]["sells"],
                    selling_buys_h24=token_data["txns"]["h24"]["buys"],
                    selling_sells_h24=token_data["txns"]["h24"]["sells"],
                    selling_volume_m5=token_data["volume"]["m5"],
                    selling_volume_h1=token_data["volume"]["h1"],
                    selling_volume_h6=token_data["volume"]["h6"],
                    selling_volume_h24=token_data["volume"]["h24"],
                    selling_price_change_m5=token_data["priceChange"]["m5"],
                    selling_price_change_h1=token_data["priceChange"]["h1"],
                    selling_price_change_h6=token_data["priceChange"]["h6"],
                    selling_price_change_h24=token_data["priceChange"]["h24"],
                    selling_liquidity=token_data["liquidity"]["usd"],
                    selling_fdv=token_data["fdv"],
                    selling_market_cap=token_data["marketCap"],
                    closing_date=timezone.now(),
                    PNL=pnl,
                    status=Status.CLOSED
                    
                )
                logger.info(f"Продажа токена {token_address} за {current_price} USD") 
  
        time.sleep(1)
            
        open_transactions = Transaction.objects.filter(status=Status.OPEN)
        buying_prices = {}
        for transaction in open_transactions:
            buying_prices[transaction.pair] = float(transaction.buying_price)
    
    return "Обновление стоимости токенов завершено"
