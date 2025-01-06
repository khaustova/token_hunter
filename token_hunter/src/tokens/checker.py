import logging
import time
import httpx
import logging
from httpx._config import Timeout
from ..utils.tokens_data import get_pairs_data, get_token_age
from ...models import Settings

logger = logging.getLogger(__name__)


class TokenChecker:
    def __init__(self, pair: str):
        self.token_data = get_pairs_data(pair)[0]
        self.token_address = self.token_data["baseToken"]["address"]
        self.token_name = self.token_data["baseToken"]["name"]
        self.settings = Settings.objects.all().first()

    def check_price(self) -> bool:
        """
        Проверяет диапазон значений цены токена.
        """
        
        if (self.settings.price_max and self.token_data["priceUsd"] > self.settings.price_max) or (
            self.settings.price_min and self.token_data["priceUsd"] < self.settings.price_min
        ):
            return False
        
        return True

    def check_age(self) -> bool:
        """
        Проверяет диапазон значений возраста токена.
        """
        
        token_age = get_token_age(self.token_data["pairCreatedAt"])
        
        if (self.settings.token_age_max and token_age > self.settings.token_age_max) or (
            self.settings.token_age_min and token_age < self.settings.price_min
        ):
            return False
        
        return True
    
    def check_transactions(self) -> bool:
        """
        Проверяет диапазон значений количества транзакций.
        """
        
        if (self.settings.transactions_buys_h1_max and self.token_data["txns"]["h1"]["buys"] > self.settings.transactions_buys_h1_max) or (
            self.settings.transactions_buys_h1_min and self.token_data["txns"]["h1"]["buys"]  < self.settings.transactions_buys_h1_min) or (
            self.settings.transactions_sells_h1_max and self.token_data["txns"]["h1"]["sells"] > self.settings.transactions_sells_h1_max) or (
            self.settings.transactions_sells_h1_min and self.token_data["txns"]["h1"]["sells"] > self.settings.transactions_sells_h1_min
        ):
            return False
        
        total_transactions = self.token_data["txns"]["h1"]["buys"] + self.token_data["txns"]["h1"]["sells"]
        
        if (self.settings.total_transactions_max and total_transactions > self.settings.total_transactions_max) or (
            self.settings.total_transactions_min and total_transactions < self.settings.total_transactions_min
        ):
            return False
        
        return True
    
    def check_transfers(self, total_transfers=None) -> bool:
        """
        Проверяет диапазон значений общего количества трансферов.
        """
        
        if (not total_transfers) or (
            self.settings.total_transfers_max and total_transfers > self.settings.total_transfers_max) or (
            self.settings.total_transfers_min and total_transfers < self.settings.total_transfers_min
        ):
            return False
        
        return True
    
    def check_volume(self) -> bool:
        """
        Проверяет диапазон значений объёма за 5 минут.
        """
        
        if (self.settings.volume_m5_max and self.token_data["volume"]["m5"] > self.settings.volume_m5_max) or (
            self.settings.volume_m5_min and self.token_data["volume"]["m5"] < self.settings.volume_m5_min
        ):
            return False
        
        return True
    
    def check_price_change(self) -> bool:
        """
        Проверяет диапазон значений изменения цены токена за 5 минут.
        """
        
        if (self.settings.price_change_m5_max and self.token_data["priceChange"]["m5"] > self.settings.price_change_m5_max) or (
            self.settings.price_change_m5_min and self.token_data["priceChange"]["m5"] < self.settings.price_change_m5_min
        ):
            return False
        
        return True
    
    def check_liquidity(self) -> bool:
        """
        Проверяет диапазон значений ликвидности.
        """
        
        if (self.settings.liquidity_max and self.token_data["liquidity"]["usd"] > self.settings.liquidity_max) or (
            self.settings.liquidity_min and self.token_data["liquidity"]["usd"] < self.settings.liquidity_min
        ):
            return False
        
        return True
    
    def check_fdv(self) -> bool:
        """
        Проверяет диапазон значений FDV.
        """
        
        if (self.settings.fdv_max and self.token_data["fdv"] > self.settings.fdv_max) or (
            self.settings.fdv_min and self.token_data["fdv"] < self.settings.fdv_min
        ):
            return False
        
        return True
    
    def check_market_cap(self) -> bool:
        """
        Проверяет диапазон значений рыночной капитализации.
        """
        
        if (self.settings.market_cap_max and self.token_data["marketCap"] > self.settings.market_cap_max) or (
            self.settings.market_cap_min and self.token_data["marketCap"] < self.settings.market_cap_min
        ):
            return False
        
        return True
        
    def check_socials(self) -> bool:
        """
        Проверяет наличие сайта, Телеграма и Твиттера.
        """
        
        data = self.token_data.get("info", None)
        if data and self.settings.is_socio:
            return True
        
        socials_info = self.get_socials_info(data)
                        
        if (self.settings.is_telegram == socials_info["is_telegram"] and 
            self.settings.is_twitter == socials_info["is_twitter"] and 
            self.settings.is_website == socials_info["is_website"]
        ):
            return True   
                        
        return False
    
    def get_socials_info(self, data: dict) -> dict:
        """
        Возвращает словарь, в котором определено наличие сайта, Твиттера 
        и Телеграма для токена token_address.
        """
        
        socials_info = {"is_telegram": False, "is_twitter": False, "is_website": False}
        
        if not data:
            return socials_info
        
        if data.get("websites"):
            socials_info["is_website"] = True
        if data.get("socials"):
            for socio in data.get("socials"):
                if socio.get("type") == "twitter":
                    socials_info["is_twitter"] = True
                elif socio.get("type") == "telegram":
                    socials_info["is_telegram"] = True
                    
        return socials_info
    
    def check_token_pairs(self) -> bool:
        """
        Проверяет наличие на бирже количество торговых пар с токеном token_address.
        """
        
        tokens_url = f"https://api.dexscreener.com/latest/dex/tokens/{self.token_address}"
        num_tokens = None
        while not num_tokens:
            time.sleep(1)
            try:
                num_tokens = httpx.get(tokens_url, timeout=Timeout(timeout=30.0)).json()["pairs"]
            except:
                continue
            
        if len(num_tokens) != 1:
            logger.debug(f"⨉ На бирже обнаружены другие токены с адресом {self.token_address}") 
            return False
        
        return True
