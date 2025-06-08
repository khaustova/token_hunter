from django import forms
from django_select2.forms import ModelSelect2TagWidget
from token_hunter.models import Settings, MonitoringRule


class SettingsSelect2TagWidget(ModelSelect2TagWidget):
    """
    Custom Select2 widget for multiple settings selection.

    Inherits from ModelSelect2TagWidget and adds functionality for:
    - Automatic creation of new settings when non-existing values are entered.
    - Filtering of existing settings.

    Attributes:
        queryset: QuerySet of all Settings objects available for selection.
    """
    queryset = Settings.objects.all()

    def value_from_datadict(self, data: dict, files: dict, name: str) -> list:
        """Processes form data.

        Args:
            data: POST request data.
            files: Uploaded files (unused).
            name: Form field name.

        Returns:
            List of IDs of selected settings.
        """
        values = set(super().value_from_datadict(data, files, name))
        pks = self.queryset.filter(**{"pk__in": list(values)}).values_list("pk", flat=True)
        pks = set(map(str, pks))
        cleaned_values = list(pks)

        for val in values - pks:
            cleaned_values.append(self.queryset.create(title=val).pk)

        return cleaned_values


class SettingsForm(forms.Form):
    """Form for configuring DEX Screener monitoring and parsing parameters.

    Fields:
        filter (CharField): Token filter input field.
        monitoring_rule (ChoiceField): Monitoring mode selection.
        settings (ModelMultipleChoiceField): Multiple settings selection.
        take_profit (FloatField): Take profit value.
        stop_loss (FloatField): Stop loss value.
        source (ChoiceField): Data source selection.
        bot (ChoiceField): Trading bot selection.

    Constants:
        CHOICES_BOTS: Available bot choices
        CHOICES_SOURCE: Available data source choices
    """
    CHOICES_BOTS = [
        ("maestro", "Maestro Sniper Bot"),
    ]
    CHOICES_SOURCE = [
        ("dexscreener", "DEX Screener"),
        ("dextools", "DEXTools")
    ]

    boosts_min = forms.IntegerField(
        initial=100,
        label="Enter minimum boost value"
    )
    boosts_max = forms.IntegerField(
        initial=500,
        label="Enter maximum boost value"
    )
    filter = forms.CharField(
        required=False,
        initial="?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=1",
        widget=forms.TextInput(
            attrs={
                "default": "Enter filter expression", 
            }
        ),
        label="Token filter expression",
    )
    monitoring_rule = forms.ChoiceField(
        choices=MonitoringRule,
        label="Monitoring mode"
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
        label="Token purchase settings",
        initial=1)
    take_profit = forms.FloatField(
        initial=60,
        label="Take profit value (%)"
    )
    stop_loss = forms.FloatField(
        initial=-20,
        label="Stop loss value (%)"
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
