import time
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 30.0


def get_pairs_data(pairs: str | list[str]) -> dict:
    """
    Возвращает данные о токена или списке токенов с DexScreener по pairs.
    """
    
    token_data_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pairs}"
    token_data = {}
    while not token_data:
        try:
            token_data = requests.get(token_data_url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)).json()["pairs"]
        except:
            logger.debug(f"Не удалось получить данные через API. Повтор попытки")
            time.sleep(1)
            continue
        
    return token_data


def get_pairs_data_for_30_more_tokens(buying_prices: dict) -> list:
    """
    Возвращает данные о более, чем 30 токенах.
    """
    
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
            
    return tokens_data


def get_token_data(token_address: str | list[str]) -> dict:
    """
    Возвращает данные о токена или списке токенов с DexScreener по адресу.
    """
    
    token_data_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    token_data = None
    while not token_data:
        try:
            token_data = requests.get(token_data_url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)).json()["pairs"]
        except:
            logger.debug(f"Не удалось получить данные через API. Повтор попытки")
            time.sleep(1)
            continue
        
    return token_data


def get_latest_boosted_tokens() -> dict:
    """
    Возвращает данные о токена или списке токенов с DexScreener.
    """
    
    boosts_tokens_url = f"https://api.dexscreener.com/token-boosts/latest/v1"
    boosted_tokens_data = None
    while not boosted_tokens_data:
        try:
            boosted_tokens_data = requests.get(boosts_tokens_url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)).json()
        except:
            logger.debug(f"Не удалось получить данные через API. Повтор попытки")
            time.sleep(1)
            continue
    
    return boosted_tokens_data


def get_token_age(created_date: datetime) -> str:
    """
    Возвращает текущий возраст токена.
    """
    
    now_date = datetime.now()
    created_date = datetime.fromtimestamp(created_date / 1000)
    token_age = (now_date - created_date).total_seconds() / 60
    token_age = round(token_age, 2)
    
    return token_age


def get_pairs_count(token_address: str) -> int:
    """
    Возвращает количество пар для токена на DexScreener.
    """
    
    try:
        pairs = requests.get("https://api.dexscreener.com/latest/dex/tokens/" + token_address).json()["pairs"]
        count = len(pairs)
    except:
        count = 0
        
    return count


def get_social_data(token_data: dict|None=None) -> dict:
    """
    Возвращает словарь, в котором определено наличие сайта, Твиттера 
    и Телеграма для токена token_address.
    """
    
    social_data = {
        "is_telegram": False, 
        "is_twitter": False, 
        "is_website": False
    }
    
    info = token_data.get("info")
    
    if not info:
        return social_data
    
    if info.get("websites"):
        social_data["is_website"] = True
        
    if info.get("socials"):
        for socio in info.get("socials"):
            if socio.get("type") == "twitter":
                social_data["is_twitter"] = True
            elif socio.get("type") == "telegram":
                social_data["is_telegram"] = True
                
    return social_data
