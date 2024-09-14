from django.contrib import admin
from .models import TopTrader, Transaction


@admin.register(TopTrader)
class TopTradersAdmin(admin.ModelAdmin):
    list_display = ("maker", "coin", "bought", "sold", "PNL")
    list_per_page = 50
    list_filter = ("coin",)
    
@admin.register(Transaction)
class TopTradersAdmin(admin.ModelAdmin):
    list_display = ("coin", "buying_price", "current_price", "selling_price", "PNL")
    list_per_page = 50