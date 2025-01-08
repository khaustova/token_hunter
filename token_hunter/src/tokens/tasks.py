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

#TOKENS_DATA = {}

@app.task
def track_tokens(TOKENS_DATA={}) -> str:
    """
    Отслеживает стоимость купленных токенов.
    Когда разница между текущей стоимостью и стоимостью покупки превышает 
    значение TAKE_PROFIT или ниже значения STOP_LOSS, происходит продажа токена.
    """
    
    step = 0
    while True:
        open_transactions = Transaction.objects.filter(status=Status.OPEN)
        if open_transactions:
            step += 1
            
            buying_prices = {transaction.pair: transaction.price_b for transaction in open_transactions}
            try:
                tokens_data = get_pairs_data(",".join(buying_prices.keys()))

                for token_data in tokens_data:
                    token_address = token_data["baseToken"]["address"]
                    pair = token_data["pairAddress"]
                    buying_price = buying_prices[pair.lower()]
                    current_price = float(token_data["priceUsd"])
                    pnl = ((current_price - buying_price) / buying_price) * 100 
                    if step == 60:
                        logger.debug(f"PNL токена {token_data["baseToken"]["name"]}: {pnl}")

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
            except:
                track_tokens.delay()
                logger.error(f"Что-то пошло не так. Перезагрузка задачи track_tockens()") 
                return 
        
        time.sleep(1)
