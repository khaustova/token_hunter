import json
import logging
from core.celery import app
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.http import require_POST
from .forms import DexscreenerForm
from .src.dex_tasks import watching_dexscreener_task, parsing_dexscreener_task
from .src.utils import get_dexscreener_worker_tasks_ids

logger = logging.getLogger(__name__)


@require_POST
def watch_dexscreener(request: HttpRequest):
    form = DexscreenerForm(request.POST)
    if form.is_valid():
        
        if "_parsing" in request.POST:
            filter = form.cleaned_data["filter"] if form.cleaned_data["filter"] else "?rankBy=trendingScoreH6&order=desc&minLiq=50000&maxAge=1"
            pages = int(form.cleaned_data["pages"]) if form.cleaned_data["pages"] else 1
            process = parsing_dexscreener_task.delay(filter, pages)
            logger.info(f"Запущена задача парсинга топа кошельков на DexScreener {process.id}")
                
        elif "_monitoring" in request.POST:
            filter = form.cleaned_data["filter"] if form.cleaned_data["filter"] else "?rankBy=trendingScoreH6&order=desc&minLiq=10000&maxAge=1"
            process = watching_dexscreener_task.delay(filter)
            logger.info(f"Запущена задача мониторинга DexScreener {process.id}")
            
        elif "_stop_monitoring" in request.POST:
            tasks_ids = get_dexscreener_worker_tasks_ids()
            task_id = tasks_ids["watching_task_id"]
                
            app.control.revoke(task_id, terminate=True)
            logger.info(f"Выполнение задачи {task_id}  мониторинга DexScreener остановлено")
            
        elif "_stop_parsing" in request.POST:
            tasks_ids = get_dexscreener_worker_tasks_ids()
            task_id = tasks_ids["parsing_task_id"]
                
            app.control.revoke(task_id, terminate=True)
            logger.info(f"Выполнение задачи {task_id} парсинга топа кошельков на DexScreener остановлено")
        
    return HttpResponseRedirect("/admin")
        

def check_coin(request: HttpRequest) -> JsonResponse:
    """
    Базовая проверка введённой в форму монеты.
    """
    
    coin = json.loads(request.body)

    return JsonResponse({"status": "done"})