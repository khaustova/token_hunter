import json
import logging
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.conf import settings
from django.views.decorators.http import require_POST
from seleniumbase import SB
from toss_a_coin.forms import DexscreenerForm
from .coin_checker import CoinChecker
from .dexscreener_worker import DexScreeneWatcher
from .parsers.dexscreener_parser import DexScreenerParser
from celery import current_app
from .tasks import watch_dexscreener_task

logger = logging.getLogger(__name__)



@require_POST
def watch_dexscreener(request: HttpRequest):
    form = DexscreenerForm(request.POST)
    if form.is_valid():
        
        if '_parsing' in request.POST:
            pages = int(form.cleaned_data["pages"]) if form.cleaned_data["pages"] else 1
            filter = form.cleaned_data["filter"] if form.cleaned_data["filter"] else ""
            with SB(uc=True, test=True, xvfb=True) as sb:
                dex_parser = DexScreenerParser(sb)
                dex_parser.parse_top_traders_from_the_pages(pages, filter)
                
        elif '_monitoring' in request.POST:
            filter = form.cleaned_data["filter"] if form.cleaned_data["filter"] else "?rankBy=trendingScoreH6&order=desc&minLiq=5000&maxAge=1"
           # watch_dexscreener_task.delay(filter)
            
            with SB(
            uc=True, 
            test=True, 
            xvfb=True,
            #headless2=True,
            extension_dir=settings.CAPTCHA_EXTENSION_DIR
        ) as sb:
                dex_parser = DexScreeneWatcher(sb, filter)
                dex_parser.watch_coins()
        
    return HttpResponseRedirect("/admin")
        

def check_coin(request: HttpRequest) -> JsonResponse:
    """
    Базовая проверка введённой в форму монеты.
    """
    
    coin = json.loads(request.body)
    coin_checker = CoinChecker()

    return JsonResponse({"status": "done"})