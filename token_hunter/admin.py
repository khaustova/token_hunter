from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeText
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from token_hunter.models import TopTrader, Transaction, Settings, Status, MonitoringRule, Mode


@admin.action(description="Delete all selected objects")
def delete_all(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    """Admin action to delete all selected objects.
    
    Args:
        modeladmin: The ModelAdmin class using this action.
        request: Current HTTP request.
        queryset: Objects selected in the admin interface.
    """
    modeladmin.model.objects.all().delete()


class TransactionResource(resources.ModelResource):
    """Resource for import/export of Transaction model data using django-import-export.
    
    Attributes:
        model: The Transaction model this resource works with.
    """
    class Meta:
        model = Transaction


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    """Admin interface for the Transaction model.
    
    Supports data import/export and provides additional features:
        - Displays Dextools link.
        - Includes button to close transactions.
    """
    list_display = ("token_name", "price_b", "opening_date", "colored_pnl", "Link", "colored_monitoring_rule", "colored_mode", "Operation")
    list_filter = ("status", "mode", "monitoring_rule", "settings")
    list_per_page = 30

    # Uncomment to add delete all transactions action
    # actions = [delete_all]
    
    change_list_template = "dashboard/transactions_list.html"
    
    def Operation(self, obj: Transaction) -> SafeText:
        """Generates a button to close an open transaction.
        
        Args:
            obj: Transaction object.
            
        Returns:
            HTML button code or None if transaction is closed.
        """
        transaction = Transaction.objects.get(pk=obj.pk)
        if transaction.status == Status.OPEN:
            link = reverse("token_hunter:sell_token", args=[obj.pk])
            html = '<input class="sell-button" type="button" onclick="location.href=\'{}\'" value="Close" />'.format(link)

            return format_html(html)

    def Link(self, obj: Transaction) -> SafeText:
        """Generates a link to the token page on DEXTools.
        
        Args:
            obj: Transaction object.
            
        Returns:
            HTML link code to DEXTools.
        """
        transaction = Transaction.objects.get(pk=obj.pk)
        href = r"https://www.dextools.io/app/en/solana/pair-explorer/" + transaction.pair
        html = f"<a href={href}>DEXTools</a>"

        return format_html(html)
    
    def colored_pnl(self, obj):
        if obj.PNL:
            if obj.PNL >= 0:
                return format_html('<span class="pnl-positive">+{} %</span>', obj.PNL)
            elif obj.PNL < 0:
                return format_html('<span class="pnl-negative">{} %</span>', obj.PNL)
        return obj.PNL
    
    def colored_monitoring_rule(self, obj):
        if obj.monitoring_rule == MonitoringRule.BOOSTED:
            return format_html('<span class="mr_boosted">{}</span>', obj.monitoring_rule.title())
        elif obj.monitoring_rule == MonitoringRule.LATEST:
            return format_html('<span class="mr_latest">{}</span>', obj.monitoring_rule.title())
        elif obj.monitoring_rule == MonitoringRule.FILTER:
            return format_html('<span class="mr_filter">{}</span>', obj.monitoring_rule.title())
        return obj.monitoring_rule
    
    def colored_mode(self, obj):
        if obj.mode == Mode.DATA_COLLECTION:
            return format_html('<span class="mode_data-collection">{}</span>', "Data Collection")
        elif obj.mode == Mode.REAL_BUY:
            return format_html('<span class="mode_real-buy">{}</span>', "Real Buy")
        elif obj.mode == Mode.SIMULATION:
            return format_html('<span class="mode_simulation">{}</span>', "Simulation")
        return obj.mode
   
    colored_pnl.short_description = "PNL"
    colored_monitoring_rule.short_description = "Type"
    colored_mode.short_description = "Mode"


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    """Admin interface for the Settings model.
    """
    list_display = ("name",)

    change_form_template = "dashboard/settings_form.html"


@admin.register(TopTrader)
class TopTradersAdmin(ImportExportModelAdmin):
    """Admin interface for the TopTrader model.
    
    Supports data import/export and sorts data by successful transaction count.
    """
    list_display = ("wallet_address", "created_date", "transaction_count", "PNL")
    list_per_page = 50

    change_list_template = "dashboard/top_traders_list.html"
    ordering = ["-transaction_count"]

    # Uncomment to add delete all top traders action
    # actions = [delete_all]
