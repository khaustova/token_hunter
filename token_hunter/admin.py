from django.core.cache import cache
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeText
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import TopTrader, Transaction, Settings, Status


@admin.action(description="Удалить все объекты")
def delete_all(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """Действие администратора для удаления всех выбранных объектов.
    
    Args:
        modeladmin: Класс ModelAdmin, использующий это действие.
        request: Текущий HTTP-запрос.
        queryset: Набор объектов, выбранных в административном интерфейсе.
    """
    modeladmin.model.objects.all().delete()


class TransactionResource(resources.ModelResource):
    """Ресурс для импорта/экспорта данных модели Transaction через django-import-export.
    
    Attributes:
        model: Модель Transaction, с которой работает ресурс.
    """
    class Meta:
        model = Transaction


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    """Интерфейс администратора для модели Transaction.
    
    Поддерживает импорт/экспорт данных и предоставляет дополнительные функции:
        - Отображение ссылки на Dextools
        - Кнопку для закрытия транзакции
    """
    list_display = ("token_name", "price_b", "opening_date", "PNL", "Dextools", "monitoring_rule", "Operation")
    list_filter = ("status", "mode", "settings")
    list_per_page = 30

    # Раскомментировать для добавления действия удаления всех транзакций:
    # actions = [delete_all]
    
    change_list_template = "dashboard/transactions_list.html"

    def Operation(self, obj: Transaction) -> SafeText:
        """Генерирует кнопку для закрытия открытой транзакции.
        
        Args:
            obj: Объект транзакции.
            
        Returns:
            HTML-код кнопки или None, если транзакция закрыта.
        """
        transaction = Transaction.objects.get(pk=obj.pk)
        if transaction.status == Status.OPEN:
            link = reverse("token_hunter:sell_token", args=[obj.pk])
            html = '<input class="sell-button" type="button" onclick="location.href=\'{}\'" value="Закрыть" />'.format(link)

            return format_html(html)

    def Dextools(self, obj: Transaction) -> SafeText:
        """Генерирует ссылку на страницу токена на DEXTools.
        
        Args:
            obj: Объект транзакции.
            
        Returns:
            HTML-код ссылки на Dextools.
        """
        transaction = Transaction.objects.get(pk=obj.pk)
        href = r"https://www.dextools.io/app/en/solana/pair-explorer/" + transaction.pair
        html = f"<a href={href}>Ссылка</a>"

        return format_html(html)


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    """Интерфейс администратора для модели Settings.
    """
    list_display = ("name",)

    change_form_template = "dashboard/settings_form.html"


@admin.register(TopTrader)
class TopTradersAdmin(ImportExportModelAdmin):
    """Интерфейс администратора для модели TopTrader.
    
    Поддерживает импорт/экспорт данных и сортирует данные по количеству успешных сделок.
    """
    list_display = ("wallet_address", "transaction_count", "PNL")
    list_per_page = 50

    change_list_template = "dashboard/top_traders_list.html"
    ordering = ["-transaction_count"]

    # Раскомментировать для добавления действия удаления всех топовых кошельков:
    # actions = [delete_all]