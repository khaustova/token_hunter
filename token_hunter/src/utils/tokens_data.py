import time
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 30.0


def get_pairs_data(pairs: str) -> dict:
    """Получает данные о паре(ах) токенов через API DEX Screener.
    
    Note:
        Автоматически повторяет запрос при неудаче с интервалом 1 секунда.
        Использует таймауты: CONNECT_TIMEOUT=5s, READ_TIMEOUT=30s.

    Args:
        pairs: Адрес(а) пары токенов.

    Returns:
        Список словарей с данными о токенах.
    """
    token_data_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pairs}"
    token_data = {}
    while not token_data:
        try:
            token_data = requests.get(
                token_data_url,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()["pairs"]
        except Exception:
            logger.debug(f"Не удалось получить данные о токене по паре(ах) через API. Повтор попытки")
            time.sleep(1)
            continue

    return token_data


def get_pairs_data_for_30_more_tokens(buying_prices: dict) -> list:
    """Получает данные о паре(ах) токенов через API DEX Screener. Если токенов меньше 30, то делает 
    единый запрос, иначе разбивает на запросы по 29 токенов и объединяет результаты всех запросов
    
    Note:
        Используется для обхода ограничения API DexScreener на количество пар в запросе.

    Args:
        buying_prices: Словарь с парами токенов в качестве ключей.

    Returns:
        Объединенный список словарей с данными о токенах.
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


def get_token_data(token_address: str) -> dict:
    """Получает данные о токене(ах) по адресу(ам) через API DexScreener.

    Args:
        token_address: Адрес(а) контракта токена.

    Returns:
        Список словарей с данными о токенах.
    """
    token_data_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    token_data = None
    while not token_data:
        try:
            token_data = requests.get(
                token_data_url, 
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()["pairs"]
        except Exception:
            logger.debug(f"Не удалось получить данные о токене по адресу(ах) контракта через API. Повтор попытки")
            time.sleep(1)
            continue

    return token_data


def get_latest_tokens() -> list:
    """Получает данные о недавно добавленных токенах через API DEX Screener.

    Returns:
        Список недавно добавленных токенов.
    """
    latest_tokens_url = f"https://api.dexscreener.com/token-profiles/latest/v1"
    latest_tokens_data = None
    while not latest_tokens_data:
        try:
            latest_tokens_data = requests.get(
                latest_tokens_url, 
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()
        except Exception:
            logger.debug(f"Не удалось получить данные о недавно добавленных токенах через API. Повтор попытки")
            time.sleep(1)
            continue

    return latest_tokens_data


def get_latest_boosted_tokens() -> dict:
    """Получает данные о недавно забустенных токенах.

    Returns:
        Список недавно забустенных токенов.
    """
    boosts_tokens_url = f"https://api.dexscreener.com/token-boosts/latest/v1"
    boosted_tokens_data = None
    while not boosted_tokens_data:
        try:
            boosted_tokens_data = requests.get(
                boosts_tokens_url, 
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()
        except Exception:
            logger.debug(f"Не удалось получить данные о забустенных токенах через API. Повтор попытки")
            time.sleep(1)
            continue
    
    return boosted_tokens_data


def get_token_age(created_date: datetime) -> float:
    """Вычисляет возраст токена в минутах.

    Args:
        created_date: Дата создания токена.

    Returns:
        Возраст токена в минутах с округлением до 2 знаков.
    """
    now_date = datetime.now()
    created_date = datetime.fromtimestamp(created_date / 1000)
    token_age = (now_date - created_date).total_seconds() / 60
    token_age = round(token_age, 2)

    return token_age


def get_pairs_count(token_address: str) -> int:
    """Получает количество торговых пар для адреса контракта токена.

    Args:
        token_address: Адрес контракта токена.

    Returns:
        Количество пар или 0 в случае ошибки.
    """
    try:
        pairs = requests.get(
            "https://api.dexscreener.com/latest/dex/tokens/" + token_address,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
        ).json()["pairs"]
        count = len(pairs)
    except Exception:
        count = 0

    return count


def get_social_data(token_data: dict|None=None) -> dict:
    """Проверяет наличие социальных сетей и сайта у токена.

    Args:
        token_data: Данные по токену, полученные через API DEX Screener.

    Returns:
        Словарь с флагами наличия:
        - is_telegram (bool): Наличие Telegram
        - is_twitter (bool): Наличие Twitter
        - is_website (bool): Наличие сайта
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
