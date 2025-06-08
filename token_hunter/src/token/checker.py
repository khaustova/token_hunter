import logging
from token_hunter.models import Settings
from token_hunter.src.utils.preprocessing_data import (
    count_no_operation, 
    count_pnl_loss, 
    get_sum_of_operation
)
from token_hunter.src.utils.tokens_data import (
    get_pairs_data,
    get_social_data,
    get_token_age,
)

logger = logging.getLogger(__name__)


class TokenChecker:
    """Validates tokens against predefined selection criteria.
    
    Attributes:
        pair: Token pair address to validate.
        check_settings: Dictionary containing setting IDs and their validation functions.
    """

    def __init__(self, pair: str, check_settings: dict):
        """Initializes the TokenChecker instance.

        Args:
            pair: Token pair address to validate.
            check_settings: Dictionary with setting IDs and validation functions in format:
                {
                    settings_id: {
                        "token_data": [list of validation functions],
                        "top_traders_data": [list of validation functions]
                    }
                }
                Each validation function dict contains:
                - "get_data_value": data extraction function.
                - "check_data": validation function.
        """
        self.pair = pair
        self.check_settings = check_settings

    def check_token(
        self,
        top_traders_data: dict | None=None,
        holders_data: dict | None=None
    ) -> int | None:
        """Validates token against selection criteria from settings.
        
        Note:
            Each validation function must return bool:
            - True: validation passed
            - False: validation failed

        Args:
            top_traders_data: Data about top wallets. Defaults to None.
            holders_data: Token holder data. Defaults to None.

        Returns:
            ID of the first matching settings profile, or None if no matches found.
        """
        token_data = get_pairs_data(self.pair)[0]

        is_check = True
        try:
            for settings_id, check in self.check_settings.items():

                for data_type, functions in check.items():

                    if not is_check:
                        break

                    if data_type == "token_data":
                        check_data = token_data
                    else:
                        check_data = top_traders_data

                    for function in functions:
                        data = function["get_data_value"](check_data)
                        is_check = function["check_data"](data)

                        if not is_check:
                            break

                if is_check:
                    return settings_id

                is_check = True
        except Exception as e:
            logger.exception(f"Token validation failed unexpectedly: {e}")

        return None


class CheckSettings:
    """Handles token selection criteria validation based on user settings."""
    
    def __init__(self, settings_id):
        """Initializes the CheckSettings instance.
        
        Args:
            settings_id: Database ID of the settings profile.
        """
        self.settings = Settings.objects.get(id=settings_id)
        
    def get_check_functions(self) -> dict:
        """Returns validation functions for different token data types.
        
        Returns:
            Dictionary containing validation functions in format:
                {
                    "token_data": [list of validation functions],
                    "top_traders_data": [list of validation functions]
                }
        """
        check_functions = {
            "token_data": self.get_check_token_data(),
            "top_traders_data": self.get_check_top_traders_data()
        }
        
        return check_functions

    def get_check_token_data(self) -> list[dict]:
        """Generates validation functions for DEX Screener API token data.
        
        Validates the following parameters:
            - Price
            - Token age
            - Buy/sell counts across timeframes
            - Trading volume
            - Price changes
            - Liquidity
            - FDV
            - Market capitalization
            - Boost status
            - Social media presence
        
        Returns:
            List of validation dictionaries, each containing:
                - check_data: Validation condition function
                - get_data_value: Data extraction function
                - settings_value: Threshold value from settings
        """
        check_token_data = [
            # Price
            {
                "check_data": lambda data_value: data_value >= self.settings.price_min,
                "get_data_value": lambda token_data: float(token_data["priceUsd"]),
                "settings_value": self.settings.price_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_max,
                "get_data_value": lambda token_data: float(token_data["priceUsd"]),
                "settings_value": self.settings.price_max
            },
            
            # Token age
            {
                "check_data": lambda data_value: data_value >= self.settings.token_age_min,
                "get_data_value": lambda token_data: get_token_age(token_data["pairCreatedAt"]),
                "settings_value": self.settings.token_age_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.token_age_max,
                "get_data_value": lambda token_data: get_token_age(token_data["pairCreatedAt"]),
                "settings_value": self.settings.token_age_max
            },
            
            # Transaction count
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_m5_min,
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["buys"],
                "settings_value": self.settings.buys_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_m5_max,             
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["buys"],
                "settings_value": self.settings.buys_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_m5_min,
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["sells"],
                "settings_value": self.settings.sells_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_m5_max,
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["sells"],
                "settings_value": self.settings.sells_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_h1_min,
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["buys"],
                "settings_value": self.settings.buys_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_h1_max,             
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["buys"],
                "settings_value": self.settings.buys_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_h1_min,
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["sells"],
                "settings_value": self.settings.sells_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_h1_max,
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["sells"],
                "settings_value": self.settings.sells_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_h6_min,
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["buys"],
                "settings_value": self.settings.buys_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_h6_max,             
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["buys"],
                "settings_value": self.settings.buys_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_h6_min,
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["sells"],
                "settings_value": self.settings.sells_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_h6_max,
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["sells"],
                "settings_value": self.settings.sells_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_h24_min,
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["buys"],
                "settings_value": self.settings.buys_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_h24_max,             
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["buys"],
                "settings_value": self.settings.buys_h24_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_h24_min,
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["sells"],
                "settings_value": self.settings.sells_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_h24_max,
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["sells"],
                "settings_value": self.settings.sells_h24_max
            },
            
            # Volume
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_m5_min,
                "get_data_value": lambda token_data: token_data["volume"]["m5"],
                "settings_value": self.settings.volume_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_m5_max,            
                "get_data_value": lambda token_data: token_data["volume"]["m5"],
                "settings_value": self.settings.volume_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_h1_min,
                "get_data_value": lambda token_data: token_data["volume"]["h1"],
                "settings_value": self.settings.volume_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_h1_max,            
                "get_data_value": lambda token_data: token_data["volume"]["h1"],
                "settings_value": self.settings.volume_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_h6_min,
                "get_data_value": lambda token_data: token_data["volume"]["h6"],
                "settings_value": self.settings.volume_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_h6_max,            
                "get_data_value": lambda token_data: token_data["volume"]["h6"],
                "settings_value": self.settings.volume_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_h24_min,
                "get_data_value": lambda token_data: token_data["volume"]["h24"],
                "settings_value": self.settings.volume_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_h24_max,            
                "get_data_value": lambda token_data: token_data["volume"]["h24"],
                "settings_value": self.settings.volume_h24_max
            },
            
            # Price change
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_m5_min,
                "get_data_value": lambda token_data: token_data["priceChange"]["m5"],
                "settings_value": self.settings.price_change_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_m5_min,                
                "get_data_value": lambda token_data: token_data["priceChange"]["m5"],
                "settings_value": self.settings.price_change_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_h1_min, 
                "get_data_value": lambda token_data: token_data["priceChange"]["h1"],
                "settings_value": self.settings.price_change_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_h1_max,                
                "get_data_value": lambda token_data: token_data["priceChange"]["h1"],
                "settings_value": self.settings.price_change_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_h6_min,
                "get_data_value": lambda token_data: token_data["priceChange"]["h6"],
                "settings_value": self.settings.price_change_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_h6_max,                
                "get_data_value": lambda token_data: token_data["priceChange"]["h6"],
                "settings_value": self.settings.price_change_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_h24_min,
                "get_data_value": lambda token_data: token_data["priceChange"]["h24"],
                "settings_value": self.settings.price_change_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_h24_max,                
                "get_data_value": lambda token_data: token_data["priceChange"]["h24"],
                "settings_value": self.settings.price_change_h24_max
            },
            
            # Liquidity
            {
                "check_data": lambda data_value: data_value >= self.settings.liquidity_min,               
                "get_data_value": lambda token_data: token_data["liquidity"]["usd"],
                "settings_value": self.settings.liquidity_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.liquidity_max,                
                "get_data_value": lambda token_data: token_data["liquidity"]["usd"],
                "settings_value": self.settings.liquidity_max
            },
            
            # FDV
            {
                "check_data": lambda data_value: data_value >= self.settings.fdv_min,                
                "get_data_value": lambda token_data: token_data["fdv"],
                "settings_value": self.settings.fdv_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.fdv_max,            
                "get_data_value": lambda token_data: token_data["fdv"],
                "settings_value": self.settings.fdv_max
            },
            
            # Market capitalization
            {
                "check_data": lambda data_value: data_value >= self.settings.market_cap_min,                
                "get_data_value": lambda token_data: token_data["marketCap"],
                "settings_value": self.settings.market_cap_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.market_cap_max,                
                "get_data_value": lambda token_data: token_data["marketCap"],
                "settings_value": self.settings.market_cap_max
            },
            
            # Boost
            {
                "check_data": lambda data_value: data_value >= self.settings.boost_min,                
                "get_data_value": lambda token_data: token_data["boosts"].get("active"),
                "settings_value": self.settings.boost_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.boost_max,                
                "get_data_value": lambda token_data: token_data["boosts"].get("active"),
                "settings_value": self.settings.boost_max
            },
            
            # Social media
            {
                "check_data": lambda social_data: any(social_data.values()),                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_socio
            },
            {
                "check_data": lambda social_data: social_data["is_telegram"],                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_telegram
            },
            {
                "check_data": lambda social_data: social_data["is_twitter"],                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_twitter
            },
            {
                "check_data": lambda social_data: social_data["is_website"],                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_website
            },

        ]

        return self.get_check_data(check_token_data)

    def get_check_top_traders_data(self) -> list[dict]:
        """Generates validation functions for top traders' transaction data.
        
        Validates:
            - Top traders' buy amounts
            - Top traders' sell amounts
            - Negative PNL counts
            - Inactive top traders
        
        Returns:
            List of validation dictionaries, each containing:
                - check_data: Validation condition function
                - get_data_value: Data extraction function
                - settings_value: Threshold value from settings
        """
        check_top_traders_data = [
            # Top traders buy amounts
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_bought_sum_min,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_bought_sum_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_bought_sum_max,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_bought_sum_max
            },
            
            # Top traders sell amounts
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_sold_sum_min,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_sold_sum_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_sold_sum_max,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_sold_sum_max
            },

            # Negative PNL counts
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_pnl_loss_min,
                "get_data_value": lambda top_traders_data: count_pnl_loss(top_traders_data["bought"], top_traders_data["sold"]),
                "settings_value": self.settings.tt_pnl_loss_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_pnl_loss_max,
                "get_data_value": lambda top_traders_data: count_pnl_loss(top_traders_data["bought"], top_traders_data["sold"]),
                "settings_value": self.settings.tt_pnl_loss_max
            },

            # Inactive top traders
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_no_bought_min,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_no_bought_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_no_bought_max,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_no_bought_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_no_sold_min,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_no_sold_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_no_sold_max,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_no_sold_max
            },
        ]

        return self.get_check_data(check_top_traders_data)


    def get_check_data(self, check_settings: list) -> list:
        """Filters validation rules to only include active settings.
        
        Args:
            check_settings: List of possible validations
            
        Returns:
            List of validations with non-None settings values
        """
        check_functions = []
        for check in check_settings:
            if check["settings_value"]:
                check_functions.append(check)

        return check_functions
