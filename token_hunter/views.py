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
    parse_dexscreener_task,
)
from .src.token.tasks import track_tokens_task
from .src.utils.tokens_data import get_pairs_data

logger = logging.getLogger(__name__)


@require_POST
def monitor_dexscreener(request: HttpRequest):
    """
    В зависимости от нажатой кнопки запускает задачу парсинга топа кошельков 
    или мониторинга DexScreener для поиска и покупки токенов.
    """
    
    form = SettingsForm(request.POST)
    if form.is_valid():
        if form.cleaned_data.get("filter"):
            filter = form.cleaned_data["filter"]  
        else:
            filter = "?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=1"
        
        if "_parsing" in request.POST: 
            process = parse_dexscreener_task.delay(filter)
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
                process = monitor_dexscreener_task.delay(settings_ids=settings_ids, filter=filter)
                logger.info(f"Запущена задача мониторинга DexScreener {process.id}")
                
        elif "_track_tokens" in request.POST:
            if form.cleaned_data.get("take_profit"):
                take_profit = form.cleaned_data["take_profit"]
            else:
                take_profit = 60
                
            if form.cleaned_data.get("stop_loss"):
                stop_loss = form.cleaned_data["stop_loss"]
            else:
                stop_loss = -20
                
            tracking_price = track_tokens_task.delay(take_profit=take_profit, stop_loss=stop_loss)
            logger.info(f"Запущена задача отслеживания стоимости {tracking_price.id} с параметрами тейк-профит: {take_profit} и стоп-лосс: {stop_loss}")
            
        
    return HttpResponseRedirect("/")


def stop_task(request: HttpRequest, task_id: str):
    """
    Останавливает задачу Celery по её id.
    """
    
    app.control.revoke(task_id, terminate=True)
    logger.info(f"Задача {task_id} остановлено")
    
    return HttpResponseRedirect("/")


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
