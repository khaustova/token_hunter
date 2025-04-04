import logging
import json
import requests
from django.conf import settings
from requests.exceptions import ReadTimeout, ConnectTimeout

logger = logging.getLogger(__name__)


def rugchek_token_with_api(token_address: str) -> dict:
    """Получает данные о токене через RugCheck API.

    Args:
        token_address: Адрес токена.

    Returns:
        Словарь с результатами проверки токена.
    """
    url = f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report"
    headers = {
        "Authorization": f"Bearer {settings.RUGCHECK_JWT_TOKEN}",
        "Accept": "application/json"
    }

    rugcheck_data = None
    for _ in range(10):
        try:
            response = requests.get(url, headers=headers, timeout=2)
            rugcheck_data = response.json()
            break
        except Exception:
            continue

    rugcheck_result = {
        "risk_level": None,
        "is_mutable_metadata": None
    }

    if not rugcheck_data:
        return rugcheck_result

    if rugcheck_data.get("tokenMeta"):
        rugcheck_result["is_mutable_metadata"] = rugcheck_data["tokenMeta"].get("mutable")

    if rugcheck_data.get("risks"):
        token_risks = rugcheck_data.get("risks")
        for risk in token_risks:
            if risk.get("name") not in settings.RUGCHECK_ACCEPTABLE_RISKS:
                rugcheck_result["risk_level"] = "Bad"
                logger.debug(f"Уровень риска токена {token_address}: {rugcheck_result["risk_level"]}, так как риск {risk.get("name")} не является допустимым")

                return rugcheck_result

    if rugcheck_data.get("score_normalised") > settings.RUGCHECK_NORMALISED_SCORE:
        rugcheck_result["risk_level"] = "Bad"
        logger.debug(f"Уровень риска токена {token_address}: {rugcheck_result["risk_level"]}, так как {rugcheck_data.get("score_normalised")} > {settings.RUGCHECK_NORMALISED_SCORE}")

        return rugcheck_result

    rugcheck_result["risk_level"] = "Good"

    return rugcheck_result
