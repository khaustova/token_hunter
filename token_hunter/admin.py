from django.contrib import admin
from django.db.models import Count
from django.shortcuts import redirect
from django.utils.html import format_html
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import TopTrader, Transaction, Settings, Status
from .src.utils.tokens_data import get_pairs_data

  
@admin.action(description="Удалить все объекты")
def delete_all(modeladmin, request, queryset):
    modeladmin.model.objects.all().delete()


class TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction  
   

@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_display = ("token_name", "price_b", "opening_date", "PNL", "link", "mode", "sell")
    list_filter = ("status", "mode", "settings")
    list_per_page = 30

    # Действие для удаления всех транзакций:
    # actions = [delete_all]
    
    resource_classes = [TransactionResource]
    
    change_list_template = 'dashboard/transactions.html'

    def sell(self, obj):
        transaction = Transaction.objects.get(pk=obj.pk)
        if transaction.status == Status.OPEN:
            link = reverse("token_hunter:sell_token", args=[obj.pk])
            html = '<input class="sell-button" type="button" onclick="location.href=\'{}\'" value="Закрыть" />'.format(link)
            
            return format_html(html)
        
    def link(self, obj):
        transaction = Transaction.objects.get(pk=obj.pk)
        href = r"https://www.dextools.io/app/en/solana/pair-explorer/" + transaction.pair
        html = f'<a href={href}>Ссылка</a>'
        
        return format_html(html)
    

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    
    change_form_template = 'dashboard/settings.html'

  
@admin.register(TopTrader)
class TopTradersAdmin(admin.ModelAdmin):
    list_display = ("wallet_address", "transaction_count", "PNL")
    list_per_page = 50
    ordering = ['-transaction_count']
    actions = [delete_all]
