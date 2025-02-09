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
    top_traders_data: dict|None=None, 
    snipers_data: dict|None=None
) -> bool:
    upd_token_data =  get_pairs_data(pair)[0]
    token_age = get_token_age(upd_token_data["pairCreatedAt"])
    
    if snipers_data and top_traders_data:
        #sns_pnl_loss = count_pnl_loss(snipers_data["bought"], snipers_data["sold"])
        tt_pnl_loss = count_pnl_loss(top_traders_data["bought"], top_traders_data["sold"])
        tt_no_bought = count_no_operation(top_traders_data["bought"])
        
        tt_bought_sum = get_sum_of_operation(top_traders_data["bought"])
        
        
        if tt_bought_sum == 0:
            return False
        
        #sns_bought_sum = get_sum(snipers_data["bought"])
        social_data = get_social_data(upd_token_data)
    
        if (upd_token_data.get("txns", {}).get("m5", {}).get("sells")
            and upd_token_data["txns"]["m5"]["sells"] < 400 
            and upd_token_data.get("txns", {}).get("h1", {}).get("sells")
            and upd_token_data["txns"]["h1"]["sells"] < 1000
            and upd_token_data.get("marketCap", 5000000) < 500000
            and upd_token_data.get("marketCap", 0) >= 30000
            and upd_token_data["boosts"].get("active") == 500
            and token_age >= 11
            and token_age <= 21
            #and sns_pnl_loss <= 20
            and tt_no_bought <= 50
            and tt_pnl_loss <= 20 
            and tt_bought_sum <= 40000
            and upd_token_data.get("priceChange", {}).get("m5")
            and upd_token_data["priceChange"]["m5"] <= 60
            and upd_token_data["priceChange"]["m5"] >= -15
            and upd_token_data["priceChange"]["h1"] >= 60
            and upd_token_data["volume"]["m5"] <= 180000
            #and sns_bought_sum <= 50000
            and any(social_data.values())
        ):

            return True
        
    return False
