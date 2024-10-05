from django.urls import path
from token_hunter import views

app_name = "token_hunter"

urlpatterns = [
    path("check_token/", views.check_token, name="check_token"),
    path("sell_token/<int:transaction_id>", views.sell_token, name="sell_token"),
    path("watch_dexscreener/", views.watch_dexscreener, name="watch_dexscreener"),
]