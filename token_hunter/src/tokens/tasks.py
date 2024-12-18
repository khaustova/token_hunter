import logging
import time
from datetime import datetime
from core.celery import app
from ..utils.tokens_data import get_pairs_data, get_token_age
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

TOKENS_DATA = {}

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
            tokens_data = get_pairs_data(tokens_str)
        else:
            tokens_amount = len(buying_prices.keys())
            tokens_data = []
            for i in range(29, tokens_amount + 1, 29):
                tokens = list(buying_prices.keys())[i-29:i]
                tokens_str = ",".join(tokens)
                tokens_data += get_pairs_data(tokens_str)
                last_step = i
                
            if last_step < tokens_amount:
                tokens = list(buying_prices.keys())[last_step:tokens_amount]
                tokens_str = ",".join(tokens)
                tokens_data += get_pairs_data(tokens_str)
        
        for token_data in tokens_data:
            token_address = token_data["baseToken"]["address"]
            pair = token_data["pairAddress"]
            buying_price = buying_prices[pair.lower()]
            current_price = float(token_data["priceUsd"])
            pnl = ((current_price - buying_price) / buying_price) * 100 
            
            TOKENS_DATA.setdefault(
                pair, 
                {
                    "is_10": None,
                    "is_20": None, 
                    "is_30": None, 
                    "is_40": None, 
                    "is_50": None
                }
            )
            
            if pnl >= 10 and not TOKENS_DATA[pair]["is_10"]:
                TOKENS_DATA[pair]["is_10"] = True
            
            if pnl >= 20 and not TOKENS_DATA[pair]["is_20"]:
                TOKENS_DATA[pair]["is_20"] = True
                
            if pnl >= 30 and not TOKENS_DATA[pair]["is_30"]:
                TOKENS_DATA[pair]["is_30"] = True
                
            if pnl >= 40 and not TOKENS_DATA[pair]["is_40"]:
                TOKENS_DATA[pair]["is_40"] = True
                
            if pnl >= 50 and not TOKENS_DATA[pair]["is_50"]:
                TOKENS_DATA[pair]["is_50"] = True
                
            if pnl >= TAKE_PROFIT or pnl <= STOP_LOSS:
                token_age = get_token_age(token_data["pairCreatedAt"])
                
                Transaction.objects.filter(token_address=token_address).update(
                    price_s=current_price,
                    token_age_s=token_age,
                    closing_date=timezone.now(),
                    PNL=pnl,
                    PNL_10=TOKENS_DATA[pair]["is_10"],
                    PNL_20=TOKENS_DATA[pair]["is_20"],
                    PNL_30=TOKENS_DATA[pair]["is_30"],
                    PNL_40=TOKENS_DATA[pair]["is_40"],
                    PNL_50=TOKENS_DATA[pair]["is_50"],
                    status=Status.CLOSED
                    
                )
                
                del TOKENS_DATA[pair]
                
                logger.info(f"Продажа токена {token_address} за {current_price} USD") 
  
        time.sleep(1)
            
        open_transactions = Transaction.objects.filter(status=Status.OPEN)
        buying_prices = {}
        for transaction in open_transactions:
            buying_prices[transaction.pair] = float(transaction.price_b)
    
    return "Обновление стоимости токенов завершено"
