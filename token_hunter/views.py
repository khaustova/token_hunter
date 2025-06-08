import logging
from core.celery import app
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib import admin
from django.db.models import Count, Sum, Max
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from redis import Redis
from redis.exceptions import LockError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from .forms import SettingsForm
from .models import Transaction, TopTrader, Status, Settings, MonitoringRule, Mode
from .serializers import TransactionSerializer
from .src.dex.tasks import (
    monitor_filtered_tokens_task, 
    monitor_boosted_tokens_task,
    monitor_latest_tokens_task,
    parse_top_traders_task,
)
from .src.token.tasks import track_tokens_task
from .src.utils.tokens_data import get_pairs_data

logger = logging.getLogger(__name__)
redis = Redis(db=1)


@require_POST
def monitor_dexscreener(request: HttpRequest) -> HttpResponseRedirect:
    """Handles POST requests to launch DEX Screener monitoring/parsing tasks.
    
    Note:
        Depending on the button pressed:
        - "_parsing": Launches parsing of top wallets.
        - "_monitoring": Launches token monitoring (3 modes):
            - BOOSTED: Monitors boosted tokens.
            - FILTER: Monitors tokens based on a filter.
            - LATEST: Monitors recently added tokens.
        - "_track_tokens": Starts tracking purchased tokens' prices.

    Args:
        request: Django HttpRequest object containing form data with settings and the pressed button.

    Returns:
        Redirects to the homepage.
    """
    form = SettingsForm(request.POST)
    if form.is_valid():
        filter = (
            form.cleaned_data.get("filter") 
            if form.cleaned_data.get("filter")
            else "?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=1"
        )
        source = (
            form.cleaned_data.get("source")
            if form.cleaned_data.get("source")
            else "dexscreener"
        )

        if "_parsing" in request.POST: 
            process = parse_top_traders_task.delay(filter, source)
            logger.info("Запущена задача парсинга топа кошельков на DexScreener %s", process.id)

        elif "_monitoring" in request.POST:
            monitoring_rule = (
                form.cleaned_data.get("monitoring_rule")
                if form.cleaned_data.get("monitoring_rule")
                else MonitoringRule.BOOSTED
            )

            settings_qs = (
                form.cleaned_data.get("settings")
                if form.cleaned_data.get("settings")
                else Settings.objects.all()
            )
            settings_ids= [settings.id for settings in settings_qs]

            if monitoring_rule == MonitoringRule.BOOSTED:
                boosts_min = (
                    form.cleaned_data.get("boosts_min")
                    if form.cleaned_data.get("boosts_min")
                    else 100
                )
                boosts_max = (
                    form.cleaned_data.get("boosts_max")
                    if form.cleaned_data.get("boosts_max")
                    else 100
                )
                process = monitor_boosted_tokens_task.delay(
                    settings_ids=settings_ids, 
                    source=source,
                    boosts_min=boosts_min,
                    boosts_max=boosts_max)
                logger.info("Запущена задача мониторинга забустенных токенов (%s)", process.id)

            elif monitoring_rule == MonitoringRule.FILTER:
                process = monitor_filtered_tokens_task.delay(settings_ids, filter, source)
                logger.info("Запущена задача мониторинга токенов по фильтру (%s)", process.id)

            elif monitoring_rule == MonitoringRule.LATEST:
                process = monitor_latest_tokens_task.delay(settings_ids, source)
                logger.info("Запущена задача мониторинга недавно добавленных токенов (%s)", process.id)

        elif "_track_tokens" in request.POST:
            take_profit = (
                form.cleaned_data.get("take_profit")
                if form.cleaned_data.get("take_profit")
                else 60
            )
            stop_loss = (
                form.cleaned_data.get("stop_loss")
                if form.cleaned_data.get("stop_loss")
                else -20
            )

            tracking_price = track_tokens_task.delay(take_profit=take_profit, stop_loss=stop_loss)
            logger.info(f"Запущена задача отслеживания стоимости {tracking_price.id} с параметрами тейк-профит: {take_profit} и стоп-лосс: {stop_loss}")

    return HttpResponseRedirect("/")


def stop_task(request: HttpRequest, task_id: str) -> HttpResponseRedirect:
    """Terminates a Celery task by its ID.
    
    Note:
        Uses forceful termination (`terminate=True`).

    Args:
        request: Django HttpRequest object.
        task_id: ID of the task to terminate.

    Returns:
        Redirects to the homepage.
    """
    app.control.revoke(task_id, terminate=True)
    logger.info(f"Задача {task_id} остановлена")
    
    return HttpResponseRedirect("/")


def group_top_traders(request: HttpRequest) -> HttpResponse:
    """Groups top wallets by transaction count and total PNL.

    Fetches a list of wallets, groups them by address, calculates total transactions 
    and cumulative PNL per wallet. Results are paginated (50 entries per page).

    Args:
        request: Django HttpRequest object containing GET parameters (e.g., page number).

    Returns:
        HttpResponse: Rendered template `top_traders_group.html`.
    """
    wallets = TopTrader.objects.values("wallet_address").annotate(
        total=Count("wallet_address"),
        total_pnl=Sum("PNL")
    ).order_by("-total")
    
    wallets = TopTrader.objects.values("wallet_address").annotate(
        total=Count("wallet_address"),
        total_pnl=Sum("PNL"),
        latest_date=Max("created_date")
    ).order_by("-total")

    paginator = Paginator(wallets, 50) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = admin.site.each_context(request)
    
    context.update({
        "page_obj": page_obj,
    })

    return render(request, "dashboard/top_traders_group.html", context)


def clear_redis_cache(request: HttpRequest) -> HttpResponseRedirect:
    """Clears Redis cache.

    Args:
        request: Django HttpRequest object containing GET parameters.

    Returns:
       Redirects to the transactions page.
    """
    for key in ("black_list", "processed_tokens"):
        try:
            with redis.lock(f"{key}_lock", timeout=10):
                if redis.exists(key):
                    redis.delete(key)
                    logger.debug(f"Ключ {key} удалён из кэша Redis")
                else:
                    logger.debug(f"Ключ {key} не существует в кэше Redis")
        except LockError:
            logger.error(f"Ошибка: блокировка для {key} не получена")

    return HttpResponseRedirect("/token_hunter/transaction")


def sell_token(request: HttpRequest, transaction_id: int) -> HttpResponseRedirect:
    """Handles manual token sale via admin panel.

    Args:
        request: Django HttpRequest object.
        transaction_id: Transaction ID in database.

    Returns:
        Redirects to the transactions page.
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
    """API class for getting PNL statistics for the last 7 days.
    
    Returns data in chart-ready format:
    {
        "dates": ["2023-01-01", "2023-01-02", ...],
        "pnl_profit": [10, 5, ...],
        "pnl_loss": [3, 7, ...]
    }
    """
    serializer_class = TransactionSerializer

    def get(self, request: Request) -> Response:
        """Handles GET request to get PNL statistics per mode.

        Args:
            request: DRF Request object.

        Returns:
            JSON response with data in format:
                {
                    "dates": ["2023-01-01", "2023-01-02", ...],
                    "pnl_profit": [10, 5, ...],
                    "pnl_loss": [3, 7, ...]
                }
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)

        modes = {
            "real_buy": Mode.REAL_BUY,
            "simulation": Mode.SIMULATION,
            "data_collection": Mode.DATA_COLLECTION
        }

        result = {}

        for mode_name, mode_value in modes.items():
            dates = [start_date + timedelta(days=i) for i in range(7)]
            date_str = [d.strftime("%Y-%m-%d") for d in dates]
            
            profit = []
            loss = []

            for day in dates:
                qs = Transaction.objects.filter(
                    mode=mode_value,
                    closing_date__date=day
                )
                profit.append(qs.filter(PNL__gte=0).count())
                loss.append(qs.filter(PNL__lt=0).count())
            
            result[mode_name] = {
                "dates": date_str,
                "profit": profit,
                "loss": loss
            }

        return Response(result)
