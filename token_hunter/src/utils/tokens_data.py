import time
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


def get_pairs_data(pairs: str | list[str]) -> dict:
    """
    Возвращает данные о токена или списке токенов с DexScreener по pairs.
    """
    
    token_data_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pairs}"
    token_data = None
    while not token_data:
        try:
            token_data = requests.get(token_data_url).json()["pairs"]
        except:
            logger.debug(f"Не удалось получить данные через API. Повтор попытки")
            time.sleep(1)
            continue
        
    return token_data


def get_token_data(token_address: str | list[str]) -> dict:
    """
    Возвращает данные о токена или списке токенов с DexScreener по адресу.
    """
    
    token_data_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    token_data = None
    while not token_data:
        try:
            token_data = requests.get(token_data_url).json()["pairs"]
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
            boosted_tokens_data = requests.get(boosts_tokens_url).json()
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


def get_socials_info(data) -> dict:
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
