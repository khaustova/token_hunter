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


    def buy_token(self, mode, snipers_data, top_traders_data):
        """
        Покупка токена.
        """
        print(1)
        token_data = get_token_data(self.pair)[0]
        token_age = get_token_age(token_data["pairCreatedAt"])
        total_transactions = token_data["txns"]["h1"]["buys"] + token_data["txns"]["h1"]["sells"]
        socials_info = self.token_checker.get_socials_info(token_data.get("info"))

        transaction, created = Transaction.objects.get_or_create(
            pair=self.pair,
            token_name=self.token_name,
            token_address=self.token_address,
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
            transactions=total_transactions,
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