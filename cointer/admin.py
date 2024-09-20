from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import TopTrader, Transaction, Status


@admin.register(TopTrader)
class TopTradersAdmin(admin.ModelAdmin):
    list_display = ("maker", "coin", "bought", "sold", "PNL")
    list_per_page = 50
    list_filter = ("coin",)
    

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("coin", "buying_price", "selling_price", "PNL", "link", "sell")
    list_per_page = 30
    list_filter = ("status",)
    change_list_template = 'dashboard/transactions.html'

    def sell(self, obj):
        transaction = Transaction.objects.get(pk=obj.pk)
        if transaction.status == Status.OPEN:
            link = reverse("cointer:sell_coin", args=[obj.pk])
            html = '<input class="sell-button" type="button" onclick="location.href=\'{}\'" value="Продать" />'.format(link)
            
            return format_html(html)
        
    def link(self, obj):
        transaction = Transaction.objects.get(pk=obj.pk)
        href = r"https://dexscreener.com/solana/" + transaction.pair
        html = f'<a href={href}>Ссылка</a>'
        
        return format_html(html)

