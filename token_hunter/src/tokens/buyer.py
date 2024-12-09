import logging
from django.conf import settings
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from telethon import TelegramClient
from .tasks import track_tokens
from .checker import TokenChecker
from ..solana.parser import SolanaParser
from ..utils.tasks_data import get_active_tasks
from ..utils.tokens_data import (
    get_pairs_data, 
    get_token_data,
    get_token_age, 
    get_socials_info
)
from ...models import Status, Transaction, Mode, Settings

logger = logging.getLogger(__name__)


class TokenBuyer:
    
    def __init__(self, pair, total_transfers=None, is_mutable_metadata=True):
        self.pair = pair
        self.total_transfers = total_transfers
        self.is_mutable_metadata = is_mutable_metadata
        
    def check_token(self):
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

    def buy_token(self, mode, snipers_data=None, top_traders_data=None, twitter_data=None, telegram_data=None):
        """
        Покупка токена.
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
        
    async def real_buy_token(self, telegram_client):    
        # app, is_created = App.objects.update_or_create(
        # api_id=settings.TELETHON_API_ID,
        # api_hash=settings.TELETHON_API_HASH
        # )
        # cs, cs_is_created = ClientSession.objects.update_or_create(
        #     name="default",
        # )
        # telegram_client = TelegramClient(DjangoSession(client_session=cs), app.api_id, app.api_hash)
        
        # await telegram_client.connect()
                
        await telegram_client.send_message("@maestro", self.token_address)

        logger.info(f"Покупка токена {self.token_name} через Maestro Bot") 