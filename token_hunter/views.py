import json
import logging
from core.celery import app
from datetime import datetime
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.response import Response
from .forms import SettingsForm
from .models import Transaction, Status, Settings, MonitoringRule, Mode
from .serializers import TransactionSerializer
from .src.dex.tasks import (
    monitor_dexscreener_task, 
    monitor_boosted_tokens_task,
    parsing_dexscreener_task,
)
from .src.token.tasks import track_tokens_task
from .src.utils.tokens_data import get_pairs_data
from .src.utils.tasks_data import get_dexscreener_worker_tasks_ids

logger = logging.getLogger(__name__)

try:
    settings = Settings.objects.all().first()
    FILTER = settings.filter
except:
    FILTER = "?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=1"


@require_POST
def monitor_dexscreener(request: HttpRequest):
    """
    В зависимости от нажатой кнопки запускает задачу парсинга топа кошельков 
    или мониторинга DexScreener для поиска и покупки токенов.
    """
    
    form = SettingsForm(request.POST)
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
            if form.cleaned_data["settings"]: 
                settings_qs = form.cleaned_data["settings"]
                monitoring_rule = form.cleaned_data["monitoring_rule"]
            else:
                settings_qs = Settings.objects.all()
                monitoring_rule = MonitoringRule.BOOSTED
                
            settings_ids= []
            for settings in settings_qs:
                    settings_ids.append(settings.id)
          
            if monitoring_rule == MonitoringRule.BOOSTED:
                monitoring = monitor_boosted_tokens_task.delay(settings_ids=settings_ids)
                logger.info(f"Запущена задача мониторинга boosted токенов на DexScreener {monitoring.id}")
                   
            elif monitoring_rule == MonitoringRule.FILTER:
                process = monitor_dexscreener_task.delay(FILTER)
                logger.info(f"Запущена задача мониторинга DexScreener {process.id}")
                

            
        elif "_stop_monitoring" in request.POST:
            tasks_ids = get_dexscreener_worker_tasks_ids()
            
            watching_task_id = tasks_ids.get("watching_task_id")
            if watching_task_id:      
                app.control.revoke(watching_task_id, terminate=True)
                logger.info(f"Остановлена задача {watching_task_id}  мониторинга DexScreener")
            
            boosted_task_id = tasks_ids.get("boosted_task_id")
            if boosted_task_id:
                app.control.revoke(boosted_task_id, terminate=True)
                logger.info(f"Остановлена задача {boosted_task_id} мониторинга boosted токенов на DexScreener")
                
        elif "_stop_parsing" in request.POST:
            tasks_ids = get_dexscreener_worker_tasks_ids()
            task_id = tasks_ids["parsing_task_id"]
                
            app.control.revoke(task_id, terminate=True)
            logger.info(f"Выполнение задачи {task_id} парсинга топа кошельков на DexScreener остановлено")
            
        
    return HttpResponseRedirect("/")


def stop_task(request: HttpRequest, task_id: str):
    """
    Останавливает задачу Celery по её id.
    """
    
    app.control.revoke(task_id, terminate=True)
    logger.info(f"Задача {task_id} остановлено")
    
    return HttpResponseRedirect("/")


def start_track_tokens_task(request: HttpRequest):
    """
    Запускает задачу отслеживания стоимости токенов.
    """
    
    tracking_price = track_tokens_task.delay()
    logger.info(f"Запущена задача отслеживания стоимости {tracking_price.id}")
    
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
    token_data = get_pairs_data(transaction.pair)[0]
    
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


class PNLCountAPI(APIView):
    """
    API для получения данных по PNL для построения графика.
    """
    
    serializer_class = TransactionSerializer

    def get(self, request):
        pnl_counts = {}
        for mode in Mode:
            pnl_profit = Transaction.objects.filter(mode=mode, PNL__gte=60).count()
            pnl_loss = Transaction.objects.filter(mode=mode, PNL__lt=60).count()
            pnl_counts[mode] = [pnl_profit, pnl_loss]
            
        return Response(pnl_counts)