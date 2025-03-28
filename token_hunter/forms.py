from django import forms
from django_select2.forms import ModelSelect2TagWidget
from token_hunter.models import Settings, MonitoringRule


class SettingsSelect2TagWidget(ModelSelect2TagWidget):
    """
    Кастомный виджет Select2 для множественного выбора настроек.

    Наследуется от ModelSelect2TagWidget и добавляет функциональность:
    - Автоматическое создание новых настроек при вводе несуществующих значений
    - Фильтрацию существующих настроек

    Attributes:
        queryset: Набор всех объектов Settings для выбора
    """
    queryset = Settings.objects.all()

    def value_from_datadict(self, data: dict, files: dict, name: str) -> list:
        """Обрабатывает данные из формы.

        Args:
            data: Данные из POST-запроса
            files: Файлы из запроса (не используются)
            name: Имя поля формы

        Returns:
            Список ID выбранных настроек
        """
        values = set(super().value_from_datadict(data, files, name))
        pks = self.queryset.filter(**{"pk__in": list(values)}).values_list("pk", flat=True)
        pks = set(map(str, pks))
        cleaned_values = list(pks)

        for val in values - pks:
            cleaned_values.append(self.queryset.create(title=val).pk)

        return cleaned_values


class SettingsForm(forms.Form):
    """Форма для настройки параметров мониторинга и парсинга DEX Screener.

    Fields:
        filter (CharField): Поле для ввода фильтра токенов.
        monitoring_rule (ChoiceField): Выбор режима мониторинга.
        settings (ModelMultipleChoiceField): Множественный выбор настроек.
        take_profit (FloatField): Значение тейк-профита.
        stop_loss (FloatField): Значение стоп-лосса.
        source (ChoiceField): Выбор источника данных.
        bot (ChoiceField): Выбор бота для покупи.

    Constants:
        CHOICES_BOTS: Варианты выбора ботов
        CHOICES_SOURCE: Варианты источников данных
    """

    CHOICES_BOTS = [
        ("maestro", "Maestro Sniper Bot"),
    ]
    CHOICES_SOURCE = [
        ("dexscreener", "DEX Screener"),
        ("dextools", "DEXTools")
    ]

    filter = forms.CharField(
        required=False,
        initial="?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=1",
        widget=forms.TextInput(
            attrs={
                "default": "Введите фильтр", 
            }
        ),
        label="Введите выражение с фильтром для токенов:",
    )
    monitoring_rule = forms.ChoiceField(
        choices=MonitoringRule,
        label="Выберите режим"
    )
    settings = forms.ModelMultipleChoiceField(
        widget=SettingsSelect2TagWidget(
            model=Settings,
            search_fields=["name__icontains",],
            attrs={
                "data-minimum-input-length": 0
            },
        ),
        queryset=Settings.objects.all(),
        required=False, 
        label="Выберите настройки для покупки токенов",
        initial=1)
    take_profit = forms.FloatField(
        initial=60,
        label="Введите значение тейк-профита"
    )
    stop_loss = forms.FloatField(
        initial=-20,
        label="Введите значение стоп-лосса"
    )
    source = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES_SOURCE,
        initial="dextools"
    )
    bot = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES_BOTS,
        initial="maestro",
    )
