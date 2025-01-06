import logging
from telethon import TelegramClient
import time
from .tasks import track_tokens
from .checker import TokenChecker
from ..utils.tasks_data import get_active_tasks
from ..utils.tokens_data import (
    get_pairs_data, 
    get_token_age, 
    get_socials_info
)
from ...models import Status, Transaction, Mode

logger = logging.getLogger(__name__)


class TokenBuyer:
    
    def __init__(
        self, 
        pair: str, 
        telegram_client: TelegramClient, 
        total_transfers: int | None=None, 
        is_mutable_metadata: bool=True
    ):
        self.pair = pair
        self.total_transfers = total_transfers
        self.is_mutable_metadata = is_mutable_metadata
        self.telegram_client = telegram_client
        
    def check_token(self) -> bool:
        """
        Базовая проверка токена.
        """
        
        token_checker = TokenChecker(self.pair)
        if (token_checker.check_price() and 
            token_checker.check_age() and
            token_checker.check_transactions() and
            token_checker.check_volume() and
            token_checker.check_price_change() and
            token_checker.check_liquidity() and
            token_checker.check_fdv() and
            token_checker.check_market_cap() and
            token_checker.check_socials()
        ):
            return True
        
        return False

    def buy_token(
        self, 
        mode: Mode, 
        snipers_data: dict | None=None, 
        top_traders_data: dict | None=None, 
        twitter_data: dict | None=None, 
        telegram_data: dict | None=None,
        price_change_data: float | None=None
    ):
        """
        Покупает токен и запускает задачу отслеживания стоимости токенов, если 
        она не запущена.
        """

        token_data = get_pairs_data(self.pair)[0]
        
        socials_info = get_socials_info(token_data.get("info"))
        token_age = get_token_age(token_data["pairCreatedAt"])
        
        if token_data.get("info"):
            socials_info = get_socials_info(token_data.get("info"))
            
        transaction, created = Transaction.objects.get_or_create(
            pair=self.pair.lower(),
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
            transfers=self.total_transfers,
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
            is_mutable_metadata = self.is_mutable_metadata,
            is_telegram=socials_info["is_telegram"],
            is_twitter=socials_info["is_twitter"],
            is_website=socials_info["is_website"],
            price_change_check=price_change_data,
            status=Status.OPEN,
            mode=mode
        )
        
        if snipers_data:
            transaction.sns_held_all = snipers_data["held_all"]
            transaction.sns_sold_some = snipers_data["sold_some"]
            transaction.sns_sold_all = snipers_data["sold_all"]
            transaction.sns_bought = snipers_data["bought"]
            transaction.sns_sold = snipers_data["sold"]
            transaction.save()
            
        if top_traders_data:
            transaction.tt_bought = top_traders_data["bought"]
            transaction.tt_sold = top_traders_data["sold"]
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
            transaction.save()

        logger.info(f"Покупка токена {token_data["baseToken"]["name"]} за {token_data["priceUsd"]} USD") 
        is_update_process = False
        try:
            active_tasks = get_active_tasks()
            for task in active_tasks:
                if task["name"] == "token_hunter.src.tokens.tasks.track_tokens":
                    is_update_process = True
                    break
        except:   
            is_update_process = False
            
        if not is_update_process:
            track_tokens.delay()
        
    async def real_buy_token(self) -> None:
        """
        Покупка токена через бот Maestro
        """  
        
        await self.telegram_client.connect()

        token_data = get_pairs_data(self.pair)[0]
        token_address = token_data["baseToken"]["address"]
        await self.telegram_client.send_message("@maestro", token_address)
        
        await self.telegram_client.disconnect()

        logger.info(f"Покупка токена {token_address} через Maestro Bot")
