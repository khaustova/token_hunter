from django.urls import path
from django.views.generic import TemplateView
from parser.views import (
    parse_top_traders
)

app_name = 'parser'

urlpatterns = [
    path('parse_top_traders/', parse_top_traders, name="parse_top_traders")
]