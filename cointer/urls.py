from django.urls import path
from cointer import views

app_name = "cointer"

urlpatterns = [
    path("check_coin/", views.check_coin, name="check_coin"),
    path("sell_coin/<int:transaction_id>", views.sell_coin, name="sell_coin"),
    path("watch_dexscreener/", views.watch_dexscreener, name="watch_dexscreener"),
]