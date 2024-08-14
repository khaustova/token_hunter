from django.http import HttpRequest, HttpResponseRedirect
from seleniumbase import SB
from .dexscreener_parser.dex_parser import DexScreenerParser

def parse_top_traders(request: HttpRequest):
    with SB(uc=True, test=True) as sb:
        dex_parser = DexScreenerParser(sb)
        dex_parser.parse_top_traders("6yhfwetd7kpubkjetf3doi6iet9qawvtkepxwgh6fbwq")
    return HttpResponseRedirect('/admin')