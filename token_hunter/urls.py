from django.urls import path
from token_hunter import views

app_name = "token_hunter"

urlpatterns = [
    path("api/pnlcounts/", views.PNLCountAPI.as_view()), 
    path("check_token/", views.check_token, name="check_token"),
    path("sell_token/<int:transaction_id>/", views.sell_token, name="sell_token"),
    path("stop_task/<str:task_id>/", views.stop_task, name="stop_task"),
    path("start_track_tokens_task/", views.start_track_tokens_task, name="start_track_tokens_task"),
    path("monitor_dexscreener/", views.monitor_dexscreener, name="monitor_dexscreener"),
]