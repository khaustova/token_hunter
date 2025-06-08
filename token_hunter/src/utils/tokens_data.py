import time
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 30.0


def get_pairs_data(pairs: str) -> list[dict]:
    """Fetches token pair data via DEX Screener API.
    
    Note:
        Automatically retries failed requests with 1-second intervals.
        Uses timeouts: CONNECT_TIMEOUT=5s, READ_TIMEOUT=30s.

    Args:
        pairs: Token pair address(es).

    Returns:
        List of dictionaries containing token data.
    """
    token_data_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pairs}"
    token_data = None
    while not token_data:
        try:
            token_data = requests.get(
                token_data_url,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()["pairs"]
        except Exception as e:
            logger.debug(f"Failed to fetch token data via API for pair(s). Retrying... Error: {e}")
            time.sleep(1)
            continue

    return token_data


def get_pairs_data_for_30_more_tokens(buying_prices: dict) -> list[dict]:
    """Fetches token pair data via DEX Screener API with batch processing.
    
    For <30 tokens: makes single API call.
    For ≥30 tokens: splits into batches of 29 tokens per call.
    
    Note:
        Works around DEX Screener API limit on pairs per request.

    Args:
        buying_prices: Dictionary with token pairs as keys.

    Returns:
        Combined list of token data dictionaries.
    """
    if len(buying_prices.keys()) < 30:
        tokens_str = ",".join(buying_prices.keys())
        return get_pairs_data(tokens_str)

    tokens_data = []
    tokens_amount = len(buying_prices.keys())
    
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
    """Fetches token data by contract address via DexScreener API.

    Args:
        token_address: Token contract address(es).

    Returns:
        List of token data dictionaries.
    """
    token_data_url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    token_data = None
    while not token_data:
        try:
            token_data = requests.get(
                token_data_url, 
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()["pairs"]
        except Exception as e:
            logger.debug(f"Failed to fetch token data by contract address via API. Retrying... Error: {e}")
            time.sleep(1)
            continue

    return token_data


def get_latest_tokens() -> list:
    """Fetches recently added tokens via DEX Screener API.

    Returns:
        List of recently added tokens.
    """
    latest_tokens_url = f"https://api.dexscreener.com/token-profiles/latest/v1"
    latest_tokens_data = None
    while not latest_tokens_data:
        try:
            latest_tokens_data = requests.get(
                latest_tokens_url, 
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()
        except Exception as e:
            logger.debug(f"Failed to fetch recently added tokens via API. Retrying... Error: {e}")
            time.sleep(1)
            continue

    return latest_tokens_data


def get_latest_boosted_tokens() -> dict:
    """Fetches recently boosted tokens data.

    Returns:
        Dictionary of recently boosted tokens.
    """
    boosts_tokens_url = f"https://api.dexscreener.com/token-boosts/latest/v1"
    boosted_tokens_data = None
    while not boosted_tokens_data:
        try:
            boosted_tokens_data = requests.get(
                boosts_tokens_url, 
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            ).json()
        except Exception as e:
            logger.debug(f"Failed to fetch boosted tokens via API. Retrying... Error: {e}")
            time.sleep(1)
            continue
    
    return boosted_tokens_data


def get_token_age(created_date: datetime) -> float:
    """Calculates token age in minutes.

    Args:
        created_timestamp: Token creation timestamp (milliseconds).

    Returns:
        Token age in minutes (rounded to 2 decimal places).
    """
    now_date = datetime.now()
    created_date = datetime.fromtimestamp(created_date / 1000)
    token_age = (now_date - created_date).total_seconds() / 60
    token_age = round(token_age, 2)

    return token_age


def get_pairs_count(token_address: str) -> int:
    """Gets trading pair count for a token contract address.

    Args:
        token_address: Token contract address.

    Returns:
        Number of trading pairs (0 if error occurs).
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
    """Checks token's social media and website presence.

    Args:
        token_data: Token data from DEX Screener API.

    Returns:
        Dictionary with presence flags:
        - is_telegram (bool): Telegram presence
        - is_twitter (bool): Twitter presence
        - is_website (bool): Website presence
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
