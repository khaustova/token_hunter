"""This is an example of settings that need to be customized for your specific needs.

To use this file, rename it from settings_example.py to settings.py.

The module contains:
- check_api_data() for initial token validation using data from DEX Screener API.
- check_settings() for comprehensive token validation after gathering additional information
  (transactions, holders, social media activity).

These functions are used for validation in token_hunter.src.dex.monitor module.
"""

from .src.utils.tokens_data import get_pairs_data, get_token_age, get_social_data
from .src.utils.preprocessing_data import count_no_operation, count_pnl_loss, get_sum_of_operation


def check_api_data(token_data: dict) -> bool:
    """Validates token data received through DEX Screener API.
    
    Notes:
        Currently contains just an example implementation.

    Args:
        token_data: Dictionary containing token data.

    Returns:
        True if token passes basic validation, False otherwise.
    """
    # Example check for at least one social media presence
    social_data = get_social_data(token_data)
    if not any(social_data.values()):
        return False
    
    # Example check for minimum buy transactions in last 5 minutes
    if token_data["txns"]["m5"]["buys"] < 100:
        return False
    
    # Default return
    return True


def check_settings(
    pair: str,
    token_info: dict | None=None,
) -> bool:
    """Performs comprehensive token validation after gathering all information.

    Validates data from both API and token page, including:
    - Top trader information.
    - Holder statistics.
    - Social media presence.
    
    Notes:
        - This is just an example implementation.
        - Data requires preprocessing before validation.

    Args:
        pair: Token pair address.
        token_info: Dictionary containing all gathered token data including:
            - top_traders_data: Top trader statistics:
                - bought (str | None): Top trader buys.
                  Example: "452.51 300.56 582.07 434.73 349.29 280.22 3860.0 1130.0...".
                - sold (str | None): Top trader sells.
                  Example: "0 2040.0 2290.0 1990.0 1790.0 0 5100.0 2270.0...".
                - unrealized (str | None): Top trader unrealized amounts.
                  Example: "2800.0 0 0 0 0 1630.0 0 0...".
                - speed (str | None): Top trader activity speed.
                  Example: "medium fast fast fast fast medium fast fast...".
            - holders_data: Token holder information:
                - percentages (float | None): Percentage held by top holders.
                  Example: "16.31 3.49 3.17 2.53 2.41 2.16 2.03 2.01 1.86 1.68 1.64 1.59 1.51 1.5 1.34 1.34 1.3 1.29 1.28 1.24".
                - liquidity (str | None): Percentage in liquidity pools.
                  Example: "17.8".
                - total (int | None): Total holder count.
                  Example: 2145.
            - trade_history_data: Recent transaction data:
                - prices (str | None): Price changes.
                  Example: "0.0008985 0.0008976 0.000898 0.0009043 0.0009123 0.0009192 0.0009066 0.0008881...".
                - date (str | None): Transaction dates.
                  Example: "May 29 00:23:06,May 29 00:22:56,May 29 00:22:49,May 29 00:22:49,May 29 00:22:48,May 29 00:22:46,May 29 00:22:40,May 29 00:22:37,...".
                - operations (str | None): Operations.
                  Example: "buy buy sell sell sell sell buy buy...".
                - trades_sum (str | None): Transaction amounts.
                  Example: "1.71 16.98 108.39 8.74 10.02 24.26 338.72...".
                - trades_makers (str | None): Trading wallets.
                  Example: "DE6uk...986T 4qjfX...sU9g G63sL...z1ck GuB9k...k69S 28VdJ...BmGq 8ZyRi...hbRo AiZoZ...NFDk GuB9k...k69S...".
                - trades_for_maker (str | None): Transactions per wallet.
                  Example: "1 1 3 99 99 3 12 99...".
                - transactions (int | None): Total transaction count.
                  Example: 6986.
            - telegram_data: Telegram channel information:
                - telegram_members (int | None): Telegram subscriber count.
                  Example: 23.
                - is_telegram_error (bool | None): Telegram link is invalid.
                  Example: False.

    Returns:
        True if token passes all validation checks, False otherwise.
    """
    # Get token data through API
    token_data = get_pairs_data(pair)[0]
    
    # Get top wallet data
    top_traders_data = token_info.get("top_traders_data")
    
    # Example token age validation
    token_age = get_token_age(token_data["pairCreatedAt"])
    if token_age <= 10:
        return False

    # Example check for top wallet data presence
    if not top_traders_data:
        return False

    # Example validation of total top wallet buy amounts
    tt_bought_sum = get_sum_of_operation(top_traders_data["bought"])
    if tt_bought_sum == 0:
        return False

    # Default return
    return True
