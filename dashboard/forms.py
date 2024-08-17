from django import forms
from .widgets import MEditorWidget

   
class MEditorFormField(forms.fields.CharField):
    
    def __init__(self, config_name='default', *args, **kwargs):
        kwargs.update({
            'widget': MEditorWidget()
        })
        super(MEditorFormField, self).__init__(*args, **kwargs)
        

class ParsingTopTradersForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Removes : as label suffix
        
    filter = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'По умолчанию парсится по рейтингу трендов за 6 часов'}),
        label="Введите фильтр для поиска монет:",
    )
    pages = forms.CharField(
        required=False, 
        widget=forms.NumberInput(attrs={'placeholder': 'По умолчанию парсится первая страница'}),
        label="Введите количество страниц:",
    )
    is_top_traders = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': '2'}),
        label="Парсинг топа трейдеров"
    )
    is_top_snipers = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': '3'}),
        label="Парсинг топа снайперов"
    )
