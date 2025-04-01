import logging
import json
import requests
from django.conf import settings
from requests.exceptions import ReadTimeout, ConnectTimeout

logger = logging.getLogger(__name__)

RUGCHECK_JWT_TOKEN = settings.RUGCHECK_JWT_TOKEN


def rugchek_token_with_api(token_address: str) -> dict:
    """Получает данные о токене через RugCheck API.

    Args:
        token_address: Адрес токена.

    Returns:
        Словарь с результатами проверки токена.
    """
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
    headers = {
        "Authorization": f"Bearer {RUGCHECK_JWT_TOKEN}",
        "Accept": "application/json"
    }

    rugcheck_data = None
    for _ in range(10):
        try:
            response = requests.get(url, headers=headers, timeout=2)
            rugcheck_data = json.loads(response.text)
            break
        except (ConnectTimeout, ReadTimeout):
            continue

    rugcheck_result = {
        "risk_level": None,
        "is_mutable_metadata": None
    }

    if not rugcheck_data:
        return rugcheck_result

    rugcheck_result["is_mutable_metadata"] = rugcheck_data["tokenMeta"].get("mutable")

    if rugcheck_data.get("risks") or rugcheck_data.get("score_normalised") > 1:
        rugcheck_result["risk_level"] = "Bad"
    else:
        rugcheck_result["risk_level"] = "Good"

    logger.debug(f"Уровень риска токена {token_address}: {rugcheck_result["risk_level"]}")

    return rugcheck_result
