from .src.utils.tokens_data import (
    get_pairs_data, 
    get_token_age, 
    get_social_data
)
from .src.utils.preprocessing_data import (
    count_no_operation, 
    count_pnl_loss, 
    get_sum_of_operation
)


def check_api_data(token_data: dict) -> bool:
    """
    Проверяет данные, полученные через DEX Screener API.
    """

    token_age = get_token_age(token_data["pairCreatedAt"])
    social_data = get_social_data(token_data)

    if all(social_data.values()):
        return True
    
    return False


def check_settings(
    pair: str | None=None,
    top_traders_data: dict | None=None, 
    snipers_data: dict | None=None,
    holders_data: dict|None=None
) -> bool:
    """
    Проверяет данные о токене, полученные как через API, так и со страницы 
    токена.
    """
    token_data = get_pairs_data(pair)[0]
    
    if not top_traders_data:
        return False

    tt_bought_sum = get_sum_of_operation(top_traders_data["bought"])
    
    if tt_bought_sum == 0:
        return False
     
    return True
