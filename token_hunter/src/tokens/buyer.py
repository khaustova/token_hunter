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


    def buy_token(self, mode, top_snipers_data, top_traders_data):
        """
        Покупка токена.
        """
        
        token_data = get_token_data(self.pair)[0]
        token_age = get_token_age(token_data["pairCreatedAt"])
        total_transactions = token_data["txns"]["h1"]["buys"] + token_data["txns"]["h1"]["sells"]
        socials_info = self.token_checker.get_socials_info(token_data.get("info"))

        transaction, created = Transaction.objects.get_or_create(
            pair=self.pair,
            token_name=self.token_name,
            token_address=self.token_address,
            buying_token_age=token_age,
            buying_price=token_data["priceUsd"],
            buying_buys_m5=token_data["txns"]["m5"]["buys"],
            buying_sells_m5=token_data["txns"]["m5"]["sells"],
            buying_buys_h1=token_data["txns"]["h1"]["buys"],
            buying_sells_h1=token_data["txns"]["h1"]["sells"],
            buying_buys_h6=token_data["txns"]["h6"]["buys"],
            buying_sells_h6=token_data["txns"]["h6"]["sells"],
            buying_buys_h24=token_data["txns"]["h24"]["buys"],
            buying_sells_h24=token_data["txns"]["h24"]["sells"],
            buying_total_transfers=self.total_transfers,
            buying_total_transactions=total_transactions,
            buying_volume_m5=token_data["volume"]["m5"],
            buying_volume_h1=token_data["volume"]["h1"],
            buying_volume_h6=token_data["volume"]["h6"],
            buying_volume_h24=token_data["volume"]["h24"],
            buying_price_change_m5=token_data["priceChange"]["m5"],
            buying_price_change_h1=token_data["priceChange"]["h1"],
            buying_price_change_h6=token_data["priceChange"]["h6"],
            buying_price_change_h24=token_data["priceChange"]["h24"],
            buying_liquidity=token_data["liquidity"]["usd"],
            buying_fdv=token_data["fdv"],
            buying_market_cap=token_data["marketCap"],
            is_telegram=socials_info["is_telegram"],
            is_twitter=socials_info["is_twitter"],
            is_website=socials_info["is_website"],
            status=Status.OPEN,
            mode=mode
        )
        
        if top_snipers_data:
            transaction.snipers_held_all = top_snipers_data["held_all"]
            transaction.snipers_sold_some = top_snipers_data["sold_some"]
            transaction.snipers_sold_all = top_snipers_data["sold_all"]
            transaction.snipers_bought_N1 = top_snipers_data["bought_1"]
            transaction.snipers_sold_N1 = top_snipers_data["sold_1"]
            transaction.snipers_bought_N2 = top_snipers_data["bought_2"]
            transaction.snipers_sold_N2 = top_snipers_data["sold_2"]
            transaction.snipers_bought_N3 = top_snipers_data["bought_3"]
            transaction.snipers_sold_N3 = top_snipers_data["sold_3"]
            transaction.snipers_bought_N4 = top_snipers_data["bought_4"]
            transaction.snipers_sold_N4 = top_snipers_data["sold_4"]
            transaction.snipers_bought_N5 = top_snipers_data["bought_5"]
            transaction.snipers_sold_N5 = top_snipers_data["sold_5"]
            transaction.snipers_bought_N6 = top_snipers_data["bought_6"]
            transaction.snipers_sold_N6 = top_snipers_data["sold_6"]
            transaction.snipers_bought_N7 = top_snipers_data["bought_7"]
            transaction.snipers_sold_N7 = top_snipers_data["sold_7"]
            transaction.snipers_bought_N8 = top_snipers_data["bought_8"]
            transaction.snipers_sold_N8 = top_snipers_data["sold_8"]
            transaction.snipers_bought_N9 = top_snipers_data["bought_9"]
            transaction.snipers_sold_N9 = top_snipers_data["sold_9"]
            transaction.snipers_bought_N10 = top_snipers_data["bought_10"]
            transaction.snipers_sold_N10 = top_snipers_data["sold_10"]
            transaction.snipers_bought_01_less = top_snipers_data["bought_01_less"]
            transaction.snipers_bought_100_less = top_snipers_data["bought_100_less"]
            transaction.snipers_bought_100_500 = top_snipers_data["bought_100_500"]
            transaction.snipers_bought_500_1000 = top_snipers_data["bought_500_1000"]
            transaction.snipers_bought_1000_2500 = top_snipers_data["bought_1000_2500"]
            transaction.snipers_bought_2500_5000 = top_snipers_data["bought_2500_5000"]
            transaction.snipers_bought_5000_more = top_snipers_data["bought_5000_more"]
            transaction.snipers_sold_01_less = top_snipers_data["sold_01_less"]
            transaction.snipers_sold_100_less = top_snipers_data["sold_100_less"]
            transaction.snipers_sold_100_500 = top_snipers_data["sold_100_500"]
            transaction.snipers_sold_500_1000 = top_snipers_data["sold_500_1000"]
            transaction.snipers_sold_1000_2500 = top_snipers_data["sold_1000_2500"]
            transaction.snipers_sold_2500_5000 = top_snipers_data["sold_2500_5000"]
            transaction.snipers_sold_5000_more = top_snipers_data["sold_5000_more"]
            transaction.snipers_pnl_100_less = top_snipers_data["pnl_100_less"]
            transaction.snipers_pnl_100_500 = top_snipers_data["pnl_100_500"]
            transaction.snipers_pnl_500_1000 = top_snipers_data["pnl_500_1000"]
            transaction.snipers_pnl_1000_2500 = top_snipers_data["pnl_1000_2500"]
            transaction.snipers_pnl_2500_5000 = top_snipers_data["pnl_2500_5000"]
            transaction.snipers_pnl_5000_more = top_snipers_data["pnl_5000_more"]
            transaction.snipers_no_bought = top_snipers_data["no_bought"]
            transaction.snipers_pnl_profit = top_snipers_data["pnl_profit"]
            transaction.snipers_pnl_loss  = top_snipers_data["pnl_loss"]
            transaction.save()
            
        if top_traders_data:
            transaction.top_traders_bought_01_less = top_traders_data["bought_01_less"]
            transaction.top_traders_bought_100_less = top_traders_data["bought_100_less"]
            transaction.top_traders_bought_100_500 = top_traders_data["bought_100_500"]
            transaction.top_traders_bought_500_1000 = top_traders_data["bought_500_1000"]
            transaction.top_traders_bought_1000_2500 = top_traders_data["bought_1000_2500"]
            transaction.top_traders_bought_2500_5000 = top_traders_data["bought_2500_5000"]
            transaction.top_traders_bought_5000_more = top_traders_data["bought_5000_more"]
            transaction.top_traders_sold_01_less = top_traders_data["sold_01_less"]
            transaction.top_traders_sold_100_less = top_traders_data["sold_100_less"]
            transaction.top_traders_sold_100_500 = top_traders_data["sold_100_500"]
            transaction.top_traders_sold_500_1000 = top_traders_data["sold_500_1000"]
            transaction.top_traders_sold_1000_2500 = top_traders_data["sold_1000_2500"]
            transaction.top_traders_sold_2500_5000 = top_traders_data["sold_2500_5000"]
            transaction.top_traders_sold_5000_more = top_traders_data["sold_5000_more"]
            transaction.top_traders_pnl_100_less = top_traders_data["pnl_100_less"]
            transaction.top_traders_pnl_100_500 = top_traders_data["pnl_100_500"]
            transaction.top_traders_pnl_500_1000 = top_traders_data["pnl_500_1000"]
            transaction.top_traders_pnl_1000_2500 = top_traders_data["pnl_1000_2500"]
            transaction.top_traders_pnl_2500_5000 = top_traders_data["pnl_2500_5000"]
            transaction.top_traders_pnl_5000_more = top_traders_data["pnl_5000_more"]
            transaction.top_traders_no_bought = top_traders_data["no_bought"]
            transaction.top_traders_no_sold = top_traders_data["no_sold"]
            transaction.top_traders_pnl_profit = top_traders_data["pnl_profit"]
            transaction.top_traders_pnl_loss = top_traders_data["pnl_loss"]
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