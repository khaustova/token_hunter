import logging
import time
from core.celery import app
from django.utils import timezone
from ..utils.tokens_data import get_pairs_data, get_token_age, get_social_data
from ..utils.preprocessing_data import get_pnl
from ...models import Transaction, Status, Settings, Mode, TopTrader

logger = logging.getLogger(__name__)

STOP_LOSS = -20
TAKE_PROFIT = 300

@app.task
def track_tokens_task(TOKENS_DATA={}) -> str:
    """
    Отслеживает стоимость купленных токенов.
    Когда разница между текущей стоимостью и стоимостью покупки превышает 
    значение TAKE_PROFIT или ниже значения STOP_LOSS, происходит продажа токена.
    """
    
    step = 0
    while True:
        try:
            open_transactions = Transaction.objects.filter(status=Status.OPEN)
        except:
            time.sleep(1)
            logger.error("Ошибка обращения к базе данных")
            continue
        
        step += 1
        if open_transactions:
            
            buying_prices = {transaction.pair: transaction.price_b for transaction in open_transactions}
            tokens_data = get_pairs_data(",".join(buying_prices.keys()))

            for token_data in tokens_data:
                token_address = token_data["baseToken"]["address"]
                pair = token_data["pairAddress"]
                buying_price = buying_prices[pair.lower()]
                current_price = float(token_data["priceUsd"])
                pnl = ((current_price - buying_price) / buying_price) * 100 
                if step == 120:
                    logger.debug(f"PNL токена {token_data["baseToken"]["name"]}: {pnl}")

                TOKENS_DATA.setdefault(
                    pair, 
                    {
                        "is_10": None,
                        "is_20": None, 
                        "is_30": None, 
                        "is_40": None, 
                        "is_50": None,
                        "is_100": None, 
                        "is_200": None, 
                        "is_loss_10": None
                    }
                )
 
                if pnl <= -10 and not TOKENS_DATA[pair]["is_loss_10"]:
                    TOKENS_DATA[pair]["is_loss_10"] = True
                
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
                    
                if pnl >= 100 and not TOKENS_DATA[pair]["is_100"]:
                    TOKENS_DATA[pair]["is_100"] = True
                    
                if pnl >= 200 and not TOKENS_DATA[pair]["is_200"]:
                    TOKENS_DATA[pair]["is_200"] = True
                    
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
                        PNL_100=TOKENS_DATA[pair]["is_100"],
                        PNL_200=TOKENS_DATA[pair]["is_200"],
                        PNL_loss_10=TOKENS_DATA[pair]["is_loss_10"],
                        status=Status.CLOSED    
                    )
                    
                    del TOKENS_DATA[pair]
                    
                    logger.info(f"Продажа токена {token_address} за {current_price} USD") 
            
        else:
            if step == 120:
                logger.debug("Нет отслеживаемых токенов")
        
        time.sleep(1)
        if step == 120:
            step = 0

@app.task
def buy_token_task(
    pair: str, 
    mode: Mode, 
    snipers_data: dict | None=None, 
    top_traders_data: dict | None=None, 
    twitter_data: dict | None=None, 
    telegram_data: dict | None=None,
    price_change: float | None=None,
    settings_id: int | None=None,
    dextscore: int | None=None,
    is_mutable_metadata: bool=False,
    transfers: int | None=None,
    boosts_ages: str | None=None 
) -> None:
    """
    Эмулирует покупку токена и сохраняет информацию о нём в базу данных.
    """
    
    logger.debug("Запущена задача эмуляции покупки монеты")
    
    token_data = get_pairs_data(pair)[0]
    token_age = get_token_age(token_data["pairCreatedAt"])
    social_data = get_social_data(token_data)
    
    if not token_data.get("priceChange", {}).get("m5"):
        logger.error("Нет данных об изменении цены за 5 минут")
        return
        
    transaction, created = Transaction.objects.get_or_create(
        pair=pair.lower(),
        token_name=token_data["baseToken"]["name"],
        token_address=token_data["baseToken"]["address"],
        token_age_b=token_age,
        price_b=token_data["priceUsd"],
        buys_m5=token_data["txns"]["m5"]["buys"],
        sells_m5=token_data["txns"]["m5"]["sells"],
        buys_h1=token_data["txns"]["h1"]["buys"],
        sells_h1=token_data["txns"]["h1"]["sells"],
        buys_h6=token_data["txns"]["h6"]["buys"],
        sells_h6=token_data["txns"]["h6"]["sells"],
        buys_h24=token_data["txns"]["h24"]["buys"],
        sells_h24=token_data["txns"]["h24"]["sells"],
        transfers=transfers,
        volume_m5=token_data["volume"]["m5"],
        volume_h1=token_data["volume"]["h1"],
        volume_h6=token_data["volume"]["h6"],
        volume_h24=token_data["volume"]["h24"],
        price_change_m5=token_data["priceChange"]["m5"],
        price_change_h1=token_data["priceChange"]["h1"],
        price_change_h6=token_data["priceChange"]["h6"],
        price_change_h24=token_data["priceChange"]["h24"],
        liquidity=token_data["liquidity"]["usd"],
        fdv=token_data["fdv"],
        market_cap=token_data["marketCap"],
        is_mutable_metadata = is_mutable_metadata,
        is_telegram=social_data["is_telegram"],
        is_twitter=social_data["is_twitter"],
        is_website=social_data["is_website"],
        dextscore=dextscore,
        price_change_check=price_change,
        status=Status.OPEN,
        mode=mode
    )
    
    if snipers_data:
        transaction.sns_held_all = snipers_data.get("held_all")
        transaction.sns_sold_some = snipers_data.get("sold_some")
        transaction.sns_sold_all = snipers_data.get("sold_all")
        transaction.sns_bought = snipers_data.get("bought")
        transaction.sns_sold = snipers_data.get("sold")
        transaction.save()
        
    if top_traders_data:
        transaction.tt_bought = top_traders_data.get("bought")
        transaction.tt_sold = top_traders_data.get("sold")
        transaction.tt_unrealized = top_traders_data.get("unrealized")
        transaction.tt_speed = top_traders_data.get("speed")
        transaction.save()
        
    if twitter_data:
        transaction.twitter_days = twitter_data.get("twitter_days")
        transaction.twitter_followers = twitter_data.get("twitter_followers")
        transaction.twitter_smart_followers = twitter_data.get("twitter_smart_followers")
        transaction.twitter_tweets = twitter_data.get("twitter_tweets")
        transaction.is_twitter_error = twitter_data.get("is_twitter_error")
        transaction.save()
        
    if telegram_data:
        transaction.telegram_members = telegram_data.get("telegram_members")
        transaction.is_telegram_error = telegram_data.get("is_telegram_error")
        transaction.save()
        
    if token_data.get("boosts"):
        transaction.boosts = token_data["boosts"].get("active")
        
        if boosts_ages:
            transaction.boosts_ages = boosts_ages
        
    if settings_id:
        transaction.settings = Settings.objects.get(id=settings_id)
        
    transaction.save()
        
    logger.info(f"Эмуляция покупки токена {token_data["baseToken"]["name"]} за {token_data["priceUsd"]} USD") 
    
    
@app.task
def save_top_traders_data_task(
    pair: str, 
    token_name: str,
    token_address: str,
    top_traders_data: dict, 
) -> None:
    """
    Сохраняет данные о топовых кошельках токена.
    """
    pnl_lst = get_pnl(top_traders_data["bought"], top_traders_data["sold"])
    top_traders_data["bought"] = [float(x) for x in top_traders_data["bought"].split(" ")]
    top_traders_data["sold"] = [float(x) for x in top_traders_data["sold"].split(" ")]
    top_traders_data["wallets"] = top_traders_data["wallets"].split(" ")
    
    
    for i in range(len(top_traders_data["bought"])):
        if top_traders_data["bought"][i] == 0 or pnl_lst[i] <= 0:
            continue

        top_trader, created = TopTrader.objects.get_or_create(
            pair=pair.lower(),
            token_name=token_name,
            token_address=token_address,
            wallet_address=top_traders_data["wallets"][i],
            bought=top_traders_data["bought"][i],
            sold=top_traders_data["sold"][i],
            PNL=pnl_lst[i],
        )
