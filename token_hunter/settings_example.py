"""Это пример настроек, которые необходимо менять под собственные нужны.

Для работы данный файл нужно переименовать из settings_example.py в settings.py.

Модуль содержит функцию check_api_data() для первичной проверки токена по данным, полученным 
через DEX Screener API и функцию check_settings() для комплексной проверки данных о токене 
после получения дополнительной информации (о транзакциях, держателях, активности в социальных сетях).

Функции используются при проверке в модуле token_hunter.src.dex.monitor.
"""

from .src.utils.tokens_data import get_pairs_data, get_token_age, get_social_data
from .src.utils.preprocessing_data import count_no_operation, count_pnl_loss, get_sum_of_operation


def check_api_data(token_data: dict) -> bool:
    """Проверяет данные о токене, полученные через DEX Screener API.
    
    Notes:
        Сейчас здесь просто пример.

    Args:
        token_data: Словарь с данными о токене.

    Returns:
        True если токен проходит базовые проверки, иначе False.
    """
    # Пример проверки на наличие хотя бы одной социальной сети:
    social_data = get_social_data(token_data)
    if not any(social_data.values()):
        return False
    
    # Пример проверки на количество покупок за последние 5 минут:
    if token_data["txns"]["m5"]["buys"] < 100:
        return False
    
    # Или пусть всегда будет True:
    return True


def check_settings(
    pair: str,
    top_traders_data: dict | None=None,
    snipers_data: dict | None=None,
    holders_data: dict | None=None,
    trade_history_data: dict | None=None,
    social_info: dict | None=None,
) -> bool:
    """Проверяет комплексные данные о токене после получения всей информации.

    Проверяет данные, полученные как через API, так и со страницы токена,
    включая информацию о топовых трейдерах, снайперах, держателях и соцсетях.
    
    Notes:
        Сейчас здесь просто пример.

    Args:
        pair: Адрес пары токена.
        top_traders_data: Данные о топовых трейдерах. По умолчанию None.
        snipers_data: Данные о снайперах. По умолчанию None.
        holders_data: Данные о держателях. По умолчанию None.
        trade_history_data: Данные о последних транзакциях. По умолчанию None.
        social_data: Данные об активности в социальных сетях. По умолчанию None.

    Returns:
        True если токен проходит все проверки, иначе False.
    """
    # Пример проверки на возраст токена
    token_data = get_pairs_data(pair)[0]
    token_age = get_token_age(token_data["pairCreatedAt"])
    if token_age <= 10:
        return False

    # Пример проверки на наличие данных по топовых кошелькам:
    if not top_traders_data:
        return False

    # Пример проверки на общую сумму покупок топовых кошельков:
    tt_bought_sum = get_sum_of_operation(top_traders_data["bought"])
    if tt_bought_sum == 0:
        return False

    # Или пусть всегда будет True:
    return True
