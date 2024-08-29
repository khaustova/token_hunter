from django.urls import path
from toss_a_coin.views import (
    parse_top_traders,
    check_coin,
    watch_dexscreener
)

app_name = "toss_a_coin"

urlpatterns = [
    path("parse_top_traders/", parse_top_traders, name="parse_top_traders"),
    path("check_coin/", check_coin, name="check_coin"),
    path("watch_dexscreener/", watch_dexscreener, name="watch_dexscreener")
]