import json
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from seleniumbase import SB
from .dex_parser import DexScreenerParser
from dashboard.forms import ParsingTopTradersForm

@require_POST
def parse_top_traders(request: HttpRequest):
    parsing_form = ParsingTopTradersForm(request.POST)
    
    if parsing_form.is_valid():
        filter = parsing_form.cleaned_data["filter"] if parsing_form.cleaned_data.get("filter") else ""
        pages = int(parsing_form.cleaned_data["pages"]) if parsing_form.cleaned_data.get("pages") else 1
        is_top_traders = parsing_form.cleaned_data["is_top_traders"]
        is_top_snipers = parsing_form.cleaned_data["is_top_snipers"]
        with SB(uc=True, test=True) as sb:
            dex_parser = DexScreenerParser(sb)
            dex_parser.parse_top_traders_from_the_pages(pages, filter, is_top_traders, is_top_snipers)
            
    return HttpResponseRedirect("/admin")
    

def check_coin(request: HttpRequest):
    coin = json.loads(request.body)

    return JsonResponse({"check_coin_result": coin, "result1": "yay"})
