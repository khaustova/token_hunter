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
        buying_prices[transaction.pair] = float(transaction.price_b)

    while open_transactions:
        if len(buying_prices.keys()) < 30:
            tokens_str = ",".join(buying_prices.keys())
            tokens_data = get_token_data(tokens_str)
        else:
            tokens_amount = len(buying_prices.keys())
            print(tokens_amount)
            tokens_data = []
            for i in range(29, tokens_amount + 1, 29):
                tokens = list(buying_prices.keys())[i-29:i]
                tokens_str = ",".join(tokens)
                tokens_data += get_token_data(tokens_str)
                last_step = i
                
            if last_step < tokens_amount:
                tokens = list(buying_prices.keys())[last_step:tokens_amount]
                tokens_str = ",".join(tokens)
                tokens_data += get_token_data(tokens_str)
        
        for token_data in tokens_data:
            token_address = token_data["baseToken"]["address"]
            pair = token_data["pairAddress"]
            buying_price = buying_prices[pair.lower()]
            current_price = float(token_data["priceUsd"])
            pnl = ((current_price - buying_price) / buying_price) * 100

            if pnl >= TAKE_PROFIT or pnl <= STOP_LOSS:
                token_age = get_token_age(token_data["pairCreatedAt"])
                
                Transaction.objects.filter(token_address=token_address).update(
                    price_s=current_price,
                    token_age_s=token_age,
                    buys_m5_s=token_data["txns"]["m5"]["buys"],
                    sells_m5_s=token_data["txns"]["m5"]["sells"],
                    buys_h1_s=token_data["txns"]["h1"]["buys"],
                    sells_h1_s=token_data["txns"]["h1"]["sells"],
                    buys_h6_s=token_data["txns"]["h6"]["buys"],
                    sells_h6_s=token_data["txns"]["h6"]["sells"],
                    buys_h24_s=token_data["txns"]["h24"]["buys"],
                    sells_h24_s=token_data["txns"]["h24"]["sells"],
                    volume_m5_s=token_data["volume"]["m5"],
                    volume_h1_s=token_data["volume"]["h1"],
                    volume_h6_s=token_data["volume"]["h6"],
                    volume_h24_s=token_data["volume"]["h24"],
                    price_change_m5_s=token_data["priceChange"]["m5"],
                    price_change_h1_s=token_data["priceChange"]["h1"],
                    price_change_h6_s=token_data["priceChange"]["h6"],
                    price_change_h24_s=token_data["priceChange"]["h24"],
                    liquidity_s=token_data["liquidity"]["usd"],
                    fdv_s=token_data["fdv"],
                    market_cap_s=token_data["marketCap"],
                    closing_date=timezone.now(),
                    PNL=pnl,
                    status=Status.CLOSED
                    
                )
                logger.info(f"Продажа токена {token_address} за {current_price} USD") 
  
        time.sleep(1)
            
        open_transactions = Transaction.objects.filter(status=Status.OPEN)
        buying_prices = {}
        for transaction in open_transactions:
            buying_prices[transaction.pair] = float(transaction.price_b)
    
    return "Обновление стоимости токенов завершено"
