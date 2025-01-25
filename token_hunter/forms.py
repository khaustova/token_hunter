from django import forms
from django.urls import reverse_lazy
from django_select2.forms import ModelSelect2TagWidget, Select2Widget
from .models import Settings, MonitoringRule        

# class DexscreenerForm(forms.Form):
#     """
#     Форма с параметрами для парсинга и мониторинга DexScreener.
#     """
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.label_suffix = ""
        
#     filter = forms.CharField(
#         required=False,
#         widget=forms.TextInput(
#             attrs={
#                 'placeholder': 'По умолчанию парсится по рейтингу трендов за 6 часов'
#             }
#         ),
#         label="Введите фильтр для поиска токена:",
#     )
#     pages = forms.CharField(
#         required=False, 
#         widget=forms.NumberInput(
#             attrs={
#                 'placeholder': 'По умолчанию парсится первая страница'
#                 }
#             ),
#         label="Введите количество страниц:",
#     )
#     monitoring_rule = forms.ChoiceField

class SettingsSelect2TagWidget(ModelSelect2TagWidget):
    queryset = Settings.objects.all()

    def value_from_datadict(self, data, files, name):
        values = set(super().value_from_datadict(data, files, name))
        pks = self.queryset.filter(**{'pk__in': list(values)}).values_list('pk', flat=True)
        pks = set(map(str, pks))
        cleaned_values = list(pks)
        for val in values - pks:
            cleaned_values.append(self.queryset.create(title=val).pk)
        return cleaned_values


class SettingsForm(forms.Form):
    monitoring_rule = forms.ChoiceField(
        choices=MonitoringRule,
        label="Выберите режим"
    )
    settings = forms.ModelMultipleChoiceField(
        widget=SettingsSelect2TagWidget(
            model=Settings,
            search_fields=['name__icontains',],
            attrs={
                'data-minimum-input-length': 0
            },
        ),
        queryset=Settings.objects.all(), 
        required=False, 
        label="Выберите настройки для покупки токенов", 
        initial=1)

    
class CheckTokenForm(forms.Form): 
    """
    Форма для базовой проверки токена.
    """
     
    token = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Введите адрес токена в сети SOLANA", 
                "id": "check-token-input", 
                "name": "token"
            }
        ),
        label="Введите адрес токена в сети SOLANA:",
    )
