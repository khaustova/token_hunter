import logging
import requests
from django.conf import settings
from moralis import sol_api
from .parsers.rugcheck_parser import RugCheckParser

MORALIS_API_KEY = settings.MORALIS_API_KEY

logger = logging.getLogger(__name__)


class CoinChecker:
    
    def __init__(self, coin_address: str):
        self.coin_address = coin_address
    
    def first_check_coin(self):
        with RugCheckParser(self.coin_address) as rug_check_parser:
            risk_level = rug_check_parser.get_risk_analysis()
            if risk_level != "Good":
                return False
            
            return True

    def check_top_traders(self):
        print(1)

