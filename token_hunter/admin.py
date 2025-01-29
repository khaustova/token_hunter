from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.utils.html import format_html
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import TopTrader, Transaction, Settings, Status


@admin.register(TopTrader)
class TopTradersAdmin(admin.ModelAdmin):
    list_display = ("wallet_address", "token_name", "bought", "sold", "PNL")
    list_per_page = 50
    list_filter = ("token_name",)


class TransactionResource(resources.ModelResource):
    class Meta:
        model = Transaction  
   

@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_display = ("token_name", "price_b", "price_s", "PNL", "PNL_20", "link", "mode", "sell")
    list_per_page = 30
    list_filter = ("status", "mode")
    resource_classes = [TransactionResource]
    
    change_list_template = 'dashboard/transactions.html'

    def sell(self, obj):
        transaction = Transaction.objects.get(pk=obj.pk)
        if transaction.status == Status.OPEN:
            link = reverse("token_hunter:sell_token", args=[obj.pk])
            html = '<input class="sell-button" type="button" onclick="location.href=\'{}\'" value="Продать" />'.format(link)
            
            return format_html(html)
        
    def link(self, obj):
        transaction = Transaction.objects.get(pk=obj.pk)
        href = r"https://dexscreener.com/solana/" + transaction.pair
        html = f'<a href={href}>Ссылка</a>'
        
        return format_html(html)
    

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    
    change_form_template = 'dashboard/settings.html'

    # def changelist_view(self, request, extra_context=None):
    #     extra_context = extra_context or {}
    #     first_obj = self.model.objects.first()
    #     if first_obj is not None:
    #         return redirect(reverse('admin:token_hunter_settings_change', args=(first_obj.pk,)))
    #     return redirect(reverse('admin:token_hunter_settings_add'))
    


