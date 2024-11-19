import json
import logging
from core.celery import app
from datetime import datetime
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.http import require_POST
from .forms import DexscreenerForm
from .models import Transaction, Status, Settings
from .src.dex.tasks import watching_dexscreener_task, parsing_dexscreener_task
from .src.utils import get_dexscreener_worker_tasks_ids, get_token_data

logger = logging.getLogger(__name__)

try:
    settings = Settings.objects.all().first()
    FILTER = settings.filter
except:
    FILTER = "?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=1"


@require_POST
def watch_dexscreener(request: HttpRequest):
    """
    В зависимости от нажатой кнопки запускает задачу парсинга топа кошельков 
    или мониторинга DexScreener для поиска и покупки токенов.
    """
    
    form = DexscreenerForm(request.POST)
    if form.is_valid():
        
        if "_parsing" in request.POST:
            if form.cleaned_data["filter"]:
                filter = form.cleaned_data["filter"]  
            else:
                filter = FILTER
            if form.cleaned_data["pages"]: 
                pages = int(form.cleaned_data["pages"])  
            else:
                pages = 1
                
            process = parsing_dexscreener_task.delay(filter, pages)
            logger.info(f"Запущена задача парсинга топа кошельков на DexScreener {process.id}")
                
        elif "_monitoring" in request.POST:
            if form.cleaned_data["filter"]:
                filter = form.cleaned_data["filter"]  
            else:
                filter = FILTER
                
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
        
    return HttpResponseRedirect("/")
        

def check_token(request: HttpRequest) -> JsonResponse:
    """
    Базовая проверка введённого в форму токена.
    """
    
    token = json.loads(request.body)

    return JsonResponse({"status": "done"})


def sell_token(request: HttpRequest, transaction_id: int):
    """
    Продажа токена из панели администратора.
    """
    
    transaction = Transaction.objects.get(pk=transaction_id)
    token_data = get_token_data(transaction.pair)[0]
    
    selling_price = float(token_data["priceUsd"])
    transaction.price_s = selling_price
    pnl = ((selling_price - transaction.price_b) / transaction.price_b) * 100
    transaction.PNL = pnl
    
    now_date = datetime.now()
    created_date = datetime.fromtimestamp(token_data["pairCreatedAt"] / 1000)
    token_age = (now_date - created_date).total_seconds() / 60
    
    transaction.token_age_s = token_age
    transaction.closing_date = datetime.now()
    transaction.status = Status.CLOSED
    transaction.save()

    return HttpResponseRedirect("/token_hunter/transaction")