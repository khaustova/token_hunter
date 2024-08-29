from django.contrib import admin
from .models import TopTrader


@admin.register(TopTrader)
class TopTradersAdmin(admin.ModelAdmin):
    list_display = ("maker", "coin", "bought", "sold", "PNL")
    list_per_page = 50
    list_filter = ("coin",)
    