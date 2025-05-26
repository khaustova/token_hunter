import logging
from datetime import datetime
from django.core.paginator import Paginator
from django.contrib import admin
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from redis import Redis
from redis.exceptions import LockError
from rest_framework.views import APIView
from rest_framework.response import Response
from core.celery import app
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
    """Обрабатывает POST-запрос для запуска задач мониторинга/парсинга DEX Screener.
    
    Note:
        В зависимости от нажатой кнопки:
        - "_parsing" - запускает парсинг топовых кошельков
        - "_monitoring" - запускает мониторинг токенов (3 режима):
            - BOOSTED: мониторинг забустенных токенов
            - FILTER: мониторинг токенов по фильтру
            - LATEST: мониторинг недавно добавленных токенов
        - "_track_tokens" - запускает отслеживание стоимости купленных токенов

    Args:
        request: Объект запроса Django, содержащий данные формы с настройками и информацию о нажатой кнопке.

    Returns:
        Перенаправление на главную страницу.
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
                process = monitor_boosted_tokens_task.delay(settings_ids, source=source)
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
    """Останавливает выполнение задачи Celery по её ID.
    
    Note:
        Использует принудительное завершение (terminate=True)

    Args:
        request: Объект запроса Django.
        task_id: ID задачи для остановки.

    Returns:
        Перенаправление на главную страницу.
    """
    app.control.revoke(task_id, terminate=True)
    logger.info(f"Задача {task_id} остановлена")
    
    return HttpResponseRedirect("/")


def group_top_traders(request: HttpRequest) -> HttpResponse:
    """Группирует топовые кошельки по количеству транзакций и суммарному PNL.

    Получает список кошельков, группирует их по адресу, вычисляет общее количество транзакций 
    и суммарный PNL для каждого кошелька. Результаты отображаются по 50 записей на странице.

    Args:
        request: Объект запроса Django, содержащий GET-параметры (включая номер страницы).

    Returns:
        Ответ с отрендеренным шаблоном top_traders_group.html.
    """
    wallets = TopTrader.objects.values("wallet_address").annotate(
        total=Count("wallet_address"),
        total_pnl=Sum("PNL")
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
    """Очищает кэш Redis.

    Args:
        request: Объект запроса Django, содержащий GET-параметры.

    Returns:
        Перенаправление на страницу транзакций
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
    """Обрабатывает ручную продажу токена через панель администратора.

    Args:
        request: Объект запроса Django
        transaction_id: ID транзакции в базе данных

    Returns:
        Перенаправление на страницу транзакций
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
    """API-класс для получения статистики по PNL транзакций по каждому режиму.

    Attributes:
        serializer_class: Сериализатор для транзакций.
    """
    serializer_class = TransactionSerializer

    def get(self, request: HttpRequest) -> Response:
        """Обрабатывает GET-запрос для получения статистики PNL по каждому режиму.

        Args:
            request: Объект запроса DRF

        Returns:
            JSON-ответ с данными в формате:
                {
                    "mode1": [profit_count, loss_count],
                    "mode2": [profit_count, loss_count],
                    ...
                }
        """
        pnl_counts = {}
        for mode in Mode:
            pnl_profit = Transaction.objects.filter(mode=mode, PNL__gte=60).count()
            pnl_loss = Transaction.objects.filter(mode=mode, PNL__lt=60).count()
            pnl_counts[mode] = [pnl_profit, pnl_loss]

        return Response(pnl_counts)
