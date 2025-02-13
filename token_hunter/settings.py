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


def check_settings(
    pair: str, 
    top_traders_data: dict | None=None, 
    snipers_data: dict | None=None,
    holders_data: dict|None=None
) -> bool:
    upd_token_data =  get_pairs_data(pair)[0]
    token_age = get_token_age(upd_token_data["pairCreatedAt"])
    
    if snipers_data and top_traders_data:
        # sns_pnl_loss = count_pnl_loss(snipers_data["bought"], snipers_data["sold"])
        # sns_bought_sum = get_sum_of_operation(snipers_data["bought"])
        
        # tt_pnl_loss = count_pnl_loss(top_traders_data["bought"], top_traders_data["sold"])
        # tt_no_bought = count_no_operation(top_traders_data["bought"])
        tt_bought_sum = get_sum_of_operation(top_traders_data["bought"])
        
        if tt_bought_sum == 0:
            return False

        social_data = get_social_data(upd_token_data)
    
        if all(social_data.values()):
            return True
        
    return False
