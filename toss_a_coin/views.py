import json
import logging
from django.http import JsonResponse, HttpRequest
from django.conf import settings
from seleniumbase import SB
from .coin_checker import CoinChecker
from .dexscreener_worker import DexScreeneWatcher
from .parsers.dexscreener_parser import DexScreenerParser

logger = logging.getLogger(__name__)


def parse_top_traders(request: HttpRequest) -> JsonResponse:
    """
    Парсит топ кошельки по заданным критериям:
    filter - фильтр в виде параметров строки запроса;
    pages - количество страниц.
    """
    
    data = json.loads(request.body)
    filter = data["filter"] if data["filter"] else ""
    pages =int(data["pages"]) if data["pages"] else 1
    
    with SB(uc=True, test=True, xvfb=True) as sb:
        dex_parser = DexScreenerParser(sb)
        dex_parser.parse_top_traders_from_the_pages(pages, filter)
            
    return JsonResponse({"status": "done"})
 
 
def check_coin(request: HttpRequest) -> JsonResponse:
    """
    Базовая проверка введённой в форму монеты.
    """
    
    coin = json.loads(request.body)
    coin_checker = CoinChecker()

    return JsonResponse({"status": "done"})


def watch_dexscreener(request: HttpRequest) -> JsonResponse:
    """ 
    Запускает мониторинг и анализ на сайте https://dexscreener.com/
    """
    
    data = json.loads(request.body)
    filter = data["filter"] if data["filter"] else "?rankBy=trendingScoreH6&order=desc&minLiq=5000&maxAge=1"
    pages =int(data["pages"]) if data["pages"] else "1"
    
    with SB(
        uc=True, 
        test=True, 
        headless=True,
        extension_dir=settings.CAPTCHA_EXTENSION_DIR
    ) as sb:
        dex_parser = DexScreeneWatcher(sb)
        dex_parser.watch_coins(pages, filter)
            
    return JsonResponse({"status": "done"})
