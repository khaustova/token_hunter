import logging
from django.conf import settings
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from telethon import TelegramClient
from .tasks import track_tokens
from .checker import TokenChecker
from ..solana.parser import SolanaParser
from ..utils import get_active_tasks, get_token_data, get_token_age
from ...models import Status, Transaction, Mode, Settings

logger = logging.getLogger(__name__)


class TokenBuyer:
    
    def __init__(self, pair, total_transfers=None):
        self.pair = pair
        self.token_data = get_token_data(self.pair)[0]
        self.token_address = self.token_data["baseToken"]["address"]
        self.token_name = self.token_data["baseToken"]["name"]
        self.total_transfers = total_transfers
        self.settings = Settings.objects.all().first()
        self.token_checker = TokenChecker(pair)
        
    def check_token(self):
        if (self.token_checker.check_price() and 
            self.token_checker.check_age() and
            self.token_checker.check_transactions() and
            self.token_checker.check_volume() and
            self.token_checker.check_price_change() and
            self.token_checker.check_liquidity() and
            self.token_checker.check_fdv() and
            self.token_checker.check_market_cap() and
            self.token_checker.check_socials()
        ):
            return True
        
        return False

    def save_transactions_history(self):
        solana_parser = SolanaParser()
        solana_parser.get_transactions_history(self.token_name, self.token_address)


    def buy_token(self, mode):
        """
        Покупка токена.
        """

        token_data = get_token_data(self.pair)[0]
        token_age = get_token_age(token_data["pairCreatedAt"])
        total_transactions = token_data["txns"]["h1"]["buys"] + token_data["txns"]["h1"]["sells"]
        socials_info = self.token_checker.get_socials_info(token_data.get("info"))

        transaction = Transaction.objects.get_or_create(
            pair=self.pair,
            token_name=self.token_name,
            token_address=self.token_address,
            buying_token_age=token_age,
            buying_price=token_data["priceUsd"],
            buying_transactions_buys_m5=token_data["txns"]["m5"]["buys"],
            buying_transactions_sells_m5=token_data["txns"]["m5"]["sells"],
            buying_transactions_buys_h1=token_data["txns"]["h1"]["buys"],
            buying_transactions_sells_h1=token_data["txns"]["h1"]["sells"],
            buying_total_transfers=self.total_transfers,
            buying_total_transactions=total_transactions,
            buying_volume_m5=token_data["volume"]["m5"],
            buying_volume_h1=token_data["volume"]["h1"],
            buying_price_change_m5=token_data["priceChange"]["m5"],
            buying_price_change_h1=token_data["priceChange"]["h1"],
            buying_liquidity=token_data["liquidity"]["usd"],
            buying_fdv=token_data["fdv"],
            buying_market_cap=token_data["marketCap"],
            is_telegram=socials_info["is_telegram"],
            is_twitter=socials_info["is_twitter"],
            is_website=socials_info["is_website"],
            status=Status.OPEN,
            mode=mode
        )
    
        logger.info(f"Покупка токена {self.token_name} за {token_data["priceUsd"]} USD") 
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
        
    async def real_buy_token(self):    
        app, is_created = App.objects.update_or_create(
        api_id=settings.TELETHON_API_ID,
        api_hash=settings.TELETHON_API_HASH
        )
        cs, cs_is_created = ClientSession.objects.update_or_create(
            name="default",
        )
        telegram_client = TelegramClient(DjangoSession(client_session=cs), app.api_id, app.api_hash)
        
        await telegram_client.connect()
                
        await telegram_client.send_message("@maestro", self.token_address)

        logger.info(f"Покупка токена {self.token_name} через Maestro Bot") 