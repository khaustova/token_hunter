import json
import logging
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.http import require_POST
from seleniumbase import SB
from toss_a_coin.forms import DexscreenerForm
from .coin_checker import CoinChecker
from .parsers.dexscreener_parser import DexScreenerParser
from core.celery import app
from .tasks import watch_dexscreener_task
from .utils import get_watch_dexscreener_task_id

logger = logging.getLogger(__name__)


@require_POST
def watch_dexscreener(request: HttpRequest):
    form = DexscreenerForm(request.POST)
    if form.is_valid():
        
        if "_parsing" in request.POST:
            pages = int(form.cleaned_data["pages"]) if form.cleaned_data["pages"] else 1
            filter = form.cleaned_data["filter"] if form.cleaned_data["filter"] else ""
            with SB(uc=True, test=True, xvfb=True) as sb:
                dex_parser = DexScreenerParser(sb)
                dex_parser.parse_top_traders_from_the_pages(pages, filter)
                
        elif "_monitoring" in request.POST:
            filter = form.cleaned_data["filter"] if form.cleaned_data["filter"] else "?rankBy=trendingScoreH6&order=desc&minLiq=5000&maxAge=1"
            watch_dexscreener_task.delay(filter)
            logger.info(f"Запущена задача мониторинга DexScreener {task_id}")
            
        elif "_stop" in request.POST:
            task_id = get_watch_dexscreener_task_id()
            app.control.revoke(task_id, terminate=True)
            logger.info(f"Выполнение задачи мониторинга DexScreener {task_id} остановлено")
        
    return HttpResponseRedirect("/admin")
        

def check_coin(request: HttpRequest) -> JsonResponse:
    """
    Базовая проверка введённой в форму монеты.
    """
    
    coin = json.loads(request.body)
    coin_checker = CoinChecker()

    return JsonResponse({"status": "done"})