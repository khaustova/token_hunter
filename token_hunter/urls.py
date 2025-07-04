from django.urls import path
from token_hunter import views

app_name = "token_hunter"

urlpatterns = [
    path("api/pnlcounts/", views.PNLCountAPI.as_view()),
    path("sell_token/<int:transaction_id>/", views.sell_token, name="sell_token"),
    path("stop_task/<str:task_id>/", views.stop_task, name="stop_task"),
    path("monitor_dexscreener/", views.monitor_dexscreener, name="monitor_dexscreener"),
    path("top_traders_group/", views.group_top_traders, name="top_traders_group"),
    path("clear_redis_cache/", views.clear_redis_cache, name="clear_redis_cache"),
]
