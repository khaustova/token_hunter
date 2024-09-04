from django.urls import path
from toss_a_coin import views

app_name = "toss_a_coin"

urlpatterns = [
    #path("parse_top_traders/", views.parse_top_traders, name="parse_top_traders"),
    path("check_coin/", views.check_coin, name="check_coin"),
    path("watch_dexscreener/", views.watch_dexscreener, name="watch_dexscreener"),
]