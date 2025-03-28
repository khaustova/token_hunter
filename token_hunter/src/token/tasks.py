import logging
import time
from django.utils import timezone
from core.celery import app
from token_hunter.src.utils.tokens_data import get_pairs_data, get_token_age, get_social_data
from token_hunter.src.utils.preprocessing_data import get_pnl
from token_hunter.models import Transaction, Status, Settings, Mode, MonitoringRule, TopTrader

logger = logging.getLogger(__name__)

TOKENS_DATA = {}


@app.task
def track_tokens_task(take_profit: float, stop_loss: float) -> str:
    """Задача отслеживания стоимости купленных токенов и выполнения продажи токена
    при достижении заданных условий.

    Когда разница между текущей стоимостью и стоимостью покупки превышает значение `take_profit`
    или опускается ниже значения `stop_loss`, происходит продажа токена.

    Args:
        take_profit: Порог прибыли для продажи токена (в процентах).
        stop_loss: Порог убытка для продажи токена (в процентах).

    Returns:
        Сообщение о завершении задачи.
    """
    while True:
        try:
            open_transactions = Transaction.objects.filter(status=Status.OPEN)
        except Exception:
            time.sleep(1)
            logger.error("Ошибка обращения к базе данных")
            continue

        if open_transactions:
            buying_prices = {transaction.pair.lower(): transaction.price_b for transaction in open_transactions}
            tokens_data = get_pairs_data(",".join(buying_prices.keys()))

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
                        "is_50": None,
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

                if pnl >= take_profit or pnl <= stop_loss:
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

@app.task
def buy_token_task(
    pair: str,
    mode: Mode,
    monitoring_rule: MonitoringRule,
    snipers_data: dict | None=None,
    top_traders_data: dict | None=None,
    holders_data: dict | None=None,
    twitter_data: dict | None=None,
    telegram_data: dict | None=None,
    settings_id: int | None=None,
    dextscore: int | None=None,
    is_mutable_metadata: bool=False,
    trade_history_data: dict | None=None,
    boosts_ages: str | None=None
) -> None:
    """Задача эмулирования покупки токена и сохранения информации о нём в базу данных.

    Args:
        pair: Адрес пары токенов.
        mode: Режим покупки.
        snipers_data: Данные о транзакциях снайперов. По умолчанию None.
        top_traders_data: Данные о транзакциях топовых кошельков. По умолчанию None.
        holders_data: Данные о держателях токенов. По умолчанию None.
        twitter_data: Данные об активности в Twitter (X). По умолчанию None.
        telegram_data: Данные об активности в Telegram. По умолчанию None.
        settings_id: ID объекта настроек, в соответствии с которым покупается токен. По умолчанию None.
        dextscore: Оценка токена на Dextools. По умолчанию None.
        is_mutable_metadata: Флаг, указывающий, изменяемы ли метаданные токена. По умолчанию False.
        trade_history_data: Данные о последних транзакциях. По умолчанию None.
        boosts_ages: Все возраста токена на момент буста. По умолчанию None.
    """
    logger.debug("Запущена задача эмуляции покупки монеты")

    token_data = get_pairs_data(pair)[0]
    token_age = get_token_age(token_data["pairCreatedAt"])
    social_data = get_social_data(token_data)

    if not token_data.get("priceChange", {}).get("m5"):
        logger.debug("Нет данных об изменении цены за 5 минут")
        return

    transaction, created = Transaction.objects.get_or_create(
        pair=token_data["pairAddress"],
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
        status=Status.OPEN,
        mode=mode,
        monitoring_rule=monitoring_rule
    )

    if snipers_data:
        transaction.sns_held_all = snipers_data.get("held_all")
        transaction.sns_sold_some = snipers_data.get("sold_some")
        transaction.sns_sold_all = snipers_data.get("sold_all")
        transaction.sns_bought = snipers_data.get("bought")
        transaction.sns_sold = snipers_data.get("sold")
        transaction.sns_unrealized = snipers_data.get("unrealized")

    if top_traders_data:
        transaction.tt_bought = top_traders_data.get("bought")
        transaction.tt_sold = top_traders_data.get("sold")
        transaction.tt_unrealized = top_traders_data.get("unrealized")
        transaction.tt_speed = top_traders_data.get("speed")
        transaction.tt_unrealized = top_traders_data.get("unrealized")

    if holders_data:
        transaction.holders_percentages = holders_data.get("percentages")
        transaction.holders_liquidity = holders_data.get("liquidity")
        transaction.holders_total = holders_data.get("total")

    if trade_history_data:
        transaction.prices = trade_history_data.get("prices")
        transaction.date = trade_history_data.get("date")
        transaction.operations = trade_history_data.get("operations")
        transaction.trades_sum = trade_history_data.get("trades_sum")
        transaction.trades_makers = trade_history_data.get("trades_makers")
        transaction.trades_for_maker = trade_history_data.get("trades_for_maker")
        transaction.transactions = trade_history_data.get("transactions")

    if twitter_data:
        transaction.twitter_days = twitter_data.get("twitter_days")
        transaction.twitter_followers = twitter_data.get("twitter_followers")
        transaction.twitter_smart_followers = twitter_data.get("twitter_smart_followers")
        transaction.twitter_tweets = twitter_data.get("twitter_tweets")
        transaction.is_twitter_error = twitter_data.get("is_twitter_error")

    if telegram_data:
        transaction.telegram_members = telegram_data.get("telegram_members")
        transaction.is_telegram_error = telegram_data.get("is_telegram_error")

    if token_data.get("boosts"):
        transaction.boosts = token_data["boosts"].get("active")
        transaction.boosts_ages = boosts_ages if boosts_ages else None

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
    """Задача сохранения информации о топовых кошельках токена в базу данных.

    Args:
        pair: Адрес пары токенов.
        token_name: Название токена.
        token_address: Адрес токена.
        top_traders_data: Данные о транзакциях топовых кошельков.
    """
    pnl_lst = get_pnl(top_traders_data["bought"], top_traders_data["sold"])
    top_traders_data["bought"] = [float(x) for x in top_traders_data["bought"].split(" ")]
    top_traders_data["sold"] = [float(x) for x in top_traders_data["sold"].split(" ")]
    top_traders_data["makers"] = top_traders_data["makers"].split(" ")

    for i in range(len(top_traders_data["bought"])):
        if top_traders_data["bought"][i] == 0 or pnl_lst[i] <= 0:
            continue

        top_trader, created = TopTrader.objects.get_or_create(
            pair=pair.lower(),
            token_name=token_name,
            token_address=token_address,
            wallet_address=top_traders_data["makers"][i],
            bought=top_traders_data["bought"][i],
            sold=top_traders_data["sold"][i],
            PNL=pnl_lst[i],
        )
