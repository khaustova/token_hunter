import json
from bs4 import BeautifulSoup
from copy import deepcopy
from django import template
from django.apps import apps
from django.db.models import Count
from django.urls import reverse
from django.http import HttpRequest
from django.utils.html import escape, format_html
from django.utils.safestring import SafeText, mark_safe
from django.utils.text import get_text_list
from django.utils.translation import gettext
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_list import result_list
from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.core.paginator import Paginator
from token_hunter.forms import SettingsForm
from token_hunter.models import TopTrader, Transaction, Status
from token_hunter.src.utils.tasks_data import get_dexscreener_worker_tasks_ids
from token_hunter.src.utils.tokens_data import get_pairs_data
from ..settings import get_settings
from ..utils import order_items

register = template.Library()


@register.simple_tag
def sidebar_status(request: HttpRequest) -> str:
    """Проверяет состояние боковой панели пользователя.

    Args:
        request: Объект запроса Django.

    Returns:
        Строка "sidebar-collapse", если панель свёрнута, иначе None.
    """
    if request.COOKIES.get("menu", "") == "closed":
        return "sidebar-collapse"

    return


@register.simple_tag
def get_customization_settings() -> dict:
    """Получает настройки кастомизации административной панели.

    Returns:
        Словарь с настройками кастомизации.
    """
    customization_settings = get_settings()

    return customization_settings


@register.simple_tag
def get_search_model() -> dict:
    """Получает параметры модели для поиска.

    Returns:
        Словарь с параметрами поиска, включая URL и название модели.
            Возвращает None, если модель поиска не настроена.
    """
    settings = get_settings()

    if not settings["search_model"]:
        return

    search_model = settings["search_model"]
    search_model_params = {}
    search_app_name, search_model_name = search_model.split(".")
    search_model_params["search_url"] = reverse(f"admin:{search_app_name}_{search_model_name}_changelist")
    search_model_meta = apps.get_registered_model(search_app_name, search_model_name)._meta
    search_model_params["search_name"] = search_model_meta.verbose_name_plural.title()

    return search_model_params


@register.simple_tag(takes_context=True)
def get_apps(context: template.Context) -> list:
    """Получает список приложений с учётом настроек кастомизации.

    Args:
        context: Контекст шаблона Django.

    Returns:
        Отфильтрованный и упорядоченный список приложений.
    """
    available_apps = deepcopy(context.get("available_apps", []))
    settings = get_settings()
    sidebar_icons = settings["sidebar_icons"]
    apps_order = settings.get("apps_order", [])
    apps_order = [app.lower() for app in apps_order]  
    apps = []

    for app in available_apps:
        app_label = app["app_label"]
        if app_label in settings["hidden_apps"]:
            continue
        models = []
        for model in app.get("models", []):
            model_name = f"{app_label}.{model["object_name"]}".lower()
            if model_name in settings["hidden_models"]:
                continue
            model["icon"] = sidebar_icons.get(model_name, "circle")
            models.append(model)

        models_reference = list(filter(lambda app: "." in app, apps_order))
        if models_reference:
            models = order_items(models,
                                 models_reference,
                                 getter=lambda app: app_label
                                 + "."
                                 + app.get("object_name").lower()
                                 )
        app["models"] = models
        apps.append(app)

    if apps_order:
        apps_reference = list(filter(lambda app: "." not in app, apps_order))
        apps = order_items(apps,
                           apps_reference,
                           getter=lambda app: app["app_label"].lower()
                           )

    return apps


@register.simple_tag(takes_context=True)
def get_sidebar_menu(context: template.Context) -> list:
    """Возвращает ссылки на приложения и модели и дополнительные ссылки для сайдбара.

    Args:
        context: Контекст шаблона Django.

    Returns:
        Список ссылок для сайдбара.
    """
    menu = get_apps(context)
    settings = get_settings()
    extra_links = settings.get("extra_links")

    if extra_links:
        for links_group in extra_links:
            for links_label, links in links_group.items():
                for app in menu:
                    app_label = app["app_label"]
                    if links_label == app_label:
                        app["models"].extend(links)

    return menu


@register.simple_tag
def action_message_to_list(action: LogEntry) -> list:
    """Форматирует сообщения о действиях пользователя.

    Args:
        action: Запись лога действия.

    Returns:
        Список отформатированных сообщений о действиях.
    """
    messages = []

    if action.change_message and action.change_message[0] == "[":
        try:
            change_message = json.loads(action.change_message)
        except json.JSONDecodeError:
            return [action.change_message]

        for sub_message in change_message:
            if "added" in sub_message:
                if sub_message["added"]:
                    sub_message["added"]["name"] = gettext(sub_message["added"]["name"])
                    messages.append({"message": (gettext("Added {name} “{object}”.").format(**sub_message["added"]))})
                else:
                    messages.append({"message": (gettext("Added."))})

            elif "changed" in sub_message:
                sub_message["changed"]["fields"] = get_text_list(
                    [gettext(field_name) for field_name in sub_message["changed"]["fields"]],
                    gettext("and"),
                    )
                if "name" in sub_message["changed"]:
                    sub_message["changed"]["name"] = gettext(sub_message["changed"]["name"])
                    messages.append({"message": (gettext("Changed {fields}.").format(**sub_message["changed"]))})
                else:
                    messages.append({"message": (gettext("Changed {fields}.").format(**sub_message["changed"]))})

            elif "deleted" in sub_message:
                sub_message["deleted"]["name"] = gettext(sub_message["deleted"]["name"])
                messages.append({"message": (gettext("Deleted “{object}”.").format(**sub_message["deleted"]))})

    return messages if len(messages) else [{"message": (gettext(action.change_message))}]


@register.filter
def bold_first_word(text: str) -> SafeText:
    """Выделяет первое слово текста жирным шрифтом.

    Args:
        text: Входной текст.

    Returns:
        Текст с первым словом в теге <strong>.
    """
    text_words = escape(text).split()

    if not len(text_words):
        return ""

    text_words[0] = "<strong>{}</strong>".format(text_words[0])
    text = " ".join([word for word in text_words])

    return mark_safe(text)


@register.simple_tag
def sort_header(header: dict, forloop: dict) -> str:
    """Генерирует CSS классы для сортировки заголовков таблицы.

    Args:
        header: Данные заголовка.
        forloop: Контекст цикла.

    Returns:
        Строка CSS классов для сортировки.
    """
    classes = []
    sorted, asc, desc = (
        header.get("sorted"),
        header.get("ascending"),
        header.get("descending"),
    )

    is_checkbox_column_conditions = (
        forloop["counter0"] == 0,
        header.get("class_attrib") == ' class="action-checkbox-column"',
    )

    if all(is_checkbox_column_conditions):
        classes.append("djn-checkbox-select-all")

    if not header["sortable"]:
        return " ".join(classes)

    if sorted and asc:
        classes.append("sorting_asc")
    elif sorted and desc:
        classes.append("sorting_desc")
    else:
        classes.append("sorting")

    return " ".join(classes)


@register.simple_tag(takes_context=True)
def get_top_traders(context: template.Context) -> str:
    """Добавляет в контекст данные о топ 100 кошельках с пагинацией.

    Args:
        context: Контекст шаблона Django.

    Returns:
        Заголовок "Топ кошельков".
    """
    top_traders = TopTrader.objects.values("wallet_address").annotate(token_count=Count("token_name")).order_by("-token_count")[:100]
    paginator = Paginator(top_traders, 10)
    request = context["request"]
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context["top_traders"] = page_obj
    
    return "Топ кошельков"


@register.simple_tag()
def get_open_transactions() -> dict:
    """Получает данные об открытых транзакциях.

    Returns:
        Словарь с данными об открытых транзакциях, включая PNL.
    """
    open_transactions_qs = Transaction.objects.filter(status=Status.OPEN)
    open_transactions = {}
    
    if open_transactions_qs:
        buying_prices = {transaction.pair: transaction.price_b for transaction in open_transactions_qs}
        
        open_transactions_pair = [transaction.pair for transaction in open_transactions_qs]
        tokens_data = get_pairs_data(",".join(open_transactions_pair))
        
        current_pnl = {}
        for token_data in tokens_data:
            pair = token_data["pairAddress"]
            buying_price = buying_prices[pair]
            current_price = float(token_data["priceUsd"])
            pnl = ((current_price - buying_price) / buying_price) * 100
            current_pnl[pair] = pnl
            
        for transaction in open_transactions_qs:
            open_transactions[transaction.pair] = {}
            open_transactions[transaction.pair]["token_name"] = transaction.token_name
            open_transactions[transaction.pair]["opening_date"] = transaction.opening_date
            open_transactions[transaction.pair]["mode"] = transaction.get_mode_display()
            open_transactions[transaction.pair]["monitoring_rule"] = transaction.get_monitoring_rule_display()
            open_transactions[transaction.pair]["current_pnl"] = round(current_pnl[transaction.pair], 2)
    
    return open_transactions


@register.simple_tag
def get_wallet_links(address: str) -> str:
    """Генерирует ссылки для анализа кошелька.

    Args:
        address: Адрес кошелька.

    Returns:
        Словарь со ссылками на Birdeye и Solscan.
    """
    return {
        "birdeye": "https://www.birdeye.so/profile/" + address,
        "solscan": "https://solscan.io/account/" + address,
    }


@register.simple_tag(takes_context=True)
def get_settings_form(context: template.Context) -> str:
    """Добавляет форму настроек мониторинга или парсинга в контекст.

    Args:
        context: Контекст шаблона Django.

    Returns:
        Заголовок "Торговля токенами Solana".
    """
    settings_form = SettingsForm()
    context["settings_form"] = settings_form
    
    return "Торговля токенами Solana"


@register.simple_tag()
def get_celery_tasks_id() -> dict:
    """Получает ID всех активных задач.

    Классифицирует задачи по типам:
    - parsing_task_id: задачи парсинга топовых трейдеров
    - track_tokens_task_id: задачи отслеживания стоимости купленных токенов
    - filter_task_id: задачи мониторинга токенов по фильтру
    - boosted_task_id: задачи мониторинга забустенных токенов

    Returns:
        Словарь с ID задач по типам в формате:
            {
                "parsing_task_id": list[str],
                "track_tokens_task_id": list[str],
                "filter_task_id": list[str],
                "boosted_task_id": list[str],
                "latest_task_id": list[str]
            }
            или None в случае ошибки.
    """
    worker_tasks_ids = get_dexscreener_worker_tasks_ids()
    return worker_tasks_ids


@register.tag(name="transactions_list")
def transactions_result_list_tag(parser, token) -> InclusionAdminNode:
    """Переопределяет шаблон для списка транзакций.

    Args:
        parser: Парсер шаблонов Django.
        token: Токен шаблона.

    Returns:
        Узел шаблона для списка транзакций.
    """
    return InclusionAdminNode(
        parser,
        token,
        func=result_list,
        template_name="transactions_list.html",
        takes_context=False,
    )


@register.simple_tag(takes_context=True)
def update_transactions_info(context: template.Context, data: list) -> SafeText:
    """Добавляет в контекст на странице списка транзакций данные о текущей цене и PNL каждой 
    открытой позиции.

    Args:
        context: Контекст шаблона Django.
        data: Список данных транзакций.

    Returns:
        Пустая строка (данные добавляются в контекст).
    """
    pairs, buying_prices = [], []
    for list in data:
        pair_td = list[0]
        pair_soup = BeautifulSoup(pair_td, "lxml")
        pair_input_element = pair_soup.find("input")
        pair = pair_input_element["aria-label"].split()[-1]
        pairs.append(pair)

        buying_price_td = list[2]
        buying_price_soup = BeautifulSoup(buying_price_td, "lxml")
        buying_price_element = buying_price_soup.find("td", {"class": "field-price_b"})
        if buying_price_element:
            buying_price = buying_price_element.text
        else:
            buying_price = None
        buying_prices.append(buying_price)
        
    pairs_str = ",".join(pairs)
    tokens_data = get_pairs_data(pairs_str)
    
    current_prices = dict(zip(pairs, [None for _ in range(len(pairs))]))
    for token_data in tokens_data:
        current_prices[token_data["pairAddress"]] = token_data["priceUsd"]
       
    current_pnls = []
    for cur_price, buy_price in zip(current_prices.values(), buying_prices):
        buy_price = buy_price.replace(",", ".")
        if cur_price:
            pnl = ((float(cur_price) - float(buy_price)) / float(buy_price)) * 100
            round_pnl = round(pnl, 2)
            current_pnls.append(round_pnl)
        else:
            current_pnls.append(None)
        
    for list, pair, c_price, c_pnl in zip(data, pairs, current_prices.values(), current_pnls):
        if Transaction.objects.filter(pair=pair, status=Status.CLOSED).exists():
            html_current_price = format_html(f"<td>-</td>")
            html_current_pnl = format_html(f"<td>-</td>")
        else:
            html_current_price = format_html(f"<td>{c_price}</td>")
            html_current_pnl = format_html(f"<td>{c_pnl}</td>")
        
        list.append(html_current_price)
        list.append(html_current_pnl)
   
    context["transactions"] = data

    return ""
