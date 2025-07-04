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
def get_customization_settings() -> dict:
    """Retrieves admin panel customization settings.

    Returns:
        Dictionary containing customization settings.
    """
    customization_settings = get_settings()

    return customization_settings


@register.simple_tag
def get_search_model() -> dict:
    """Retrieves search model parameters.

    Returns:
        Dictionary containing search parameters including URL and model name.
        Returns None if search model is not configured.
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
    """Retrieves applications list considering customization settings.

    Args:
        context: Django template context.

    Returns:
        Filtered and ordered list of applications.
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
    """Returns application/model links and additional sidebar links.

    Args:
        context: Django template context.

    Returns:
        List of sidebar links.
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
    """Formats user action log messages.

    Args:
        action: Action log entry.

    Returns:
        List of formatted action messages.
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
    """Highlights the first word of text in bold.

    Args:
        text: Input text.

    Returns:
        Text with first word wrapped in <strong> tag.
    """
    text_words = escape(text).split()

    if not len(text_words):
        return ""

    text_words[0] = "<strong>{}</strong>".format(text_words[0])
    text = " ".join([word for word in text_words])

    return mark_safe(text)


@register.simple_tag
def sort_header(header: dict, forloop: dict) -> str:
    """Generates CSS classes for table sorting headers.

    Args:
        header: Header data dictionary.
        forloop: Loop context dictionary.

    Returns:
        String of CSS classes for sorting styling.
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
    """Adds paginated top 100 wallet data to template context.

    Args:
        context: Django template context.

    Returns:
        The string "Top Wallets" for template display.
    """
    top_traders = TopTrader.objects.values("wallet_address").annotate(token_count=Count("token_name")).order_by("-token_count")[:100]
    paginator = Paginator(top_traders, 10)
    request = context["request"]
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context["top_traders"] = page_obj
    
    return "Top Wallets"


@register.simple_tag()
def get_open_transactions() -> dict:
    """Retrieves data about open transactions including PNL.

    Returns:
        Dictionary containing open transaction data with PNL calculations.
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
    """Generates wallet analysis links for blockchain explorers.

    Args:
        address: Wallet address string.

    Returns:
        Dictionary with links to Birdeye and Solscan explorers.
    """
    return {
        "birdeye": "https://www.birdeye.so/profile/" + address,
        "solscan": "https://solscan.io/account/" + address,
    }


@register.simple_tag(takes_context=True)
def get_settings_form(context: template.Context) -> str:
    """Adds monitoring/parsing settings form to template context.

    Args:
        context: Django template context.

    Returns:
        The string "DEX Exchange Monitoring" for template display.
    """
    settings_form = SettingsForm()
    context["settings_form"] = settings_form
    
    return "DEX Exchange Monitoring"


@register.simple_tag()
def get_celery_tasks_id() -> dict:
    """Retrieves IDs of all active Celery tasks categorized by type.

    Task categories:
    - parsing_task_id: Top traders parsing tasks.
    - track_tokens_task_id: Purchased tokens tracking tasks.
    - filter_task_id: Token filter monitoring tasks.
    - boosted_task_id: Boosted tokens monitoring tasks.

    Returns:
        Dictionary with task IDs organized by category:
            {
                "parsing_task_id": list[str],
                "track_tokens_task_id": list[str],
                "filter_task_id": list[str],
                "boosted_task_id": list[str],
                "latest_task_id": list[str]
            }
        Returns None on error.
    """
    worker_tasks_ids = get_dexscreener_worker_tasks_ids()
    return worker_tasks_ids


@register.simple_tag(takes_context=True)
def update_transactions_info(context: template.Context, data: list) -> SafeText:
    """Adds current price and PNL data for open positions to transactions list context.

    Args:
        context: Django template context.
        data: List of transaction data.

    Returns:
        Empty string (modifies context directly).
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
