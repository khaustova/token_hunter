from django import forms
        

class DexscreenerForm(forms.Form):
    """
    Форма с параметрами для парсинга и мониторинга DexScreener.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        
    filter = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'По умолчанию парсится по рейтингу трендов за 6 часов'
            }
        ),
        label="Введите фильтр для поиска токена:",
    )
    pages = forms.CharField(
        required=False, 
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'По умолчанию парсится первая страница'
                }
            ),
        label="Введите количество страниц:",
    )
    
class CheckTokenForm(forms.Form): 
    """
    Форма для базовой проверки токена.
    """
     
    token = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Сейчас поддерживается только сеть SOLANA", 
                "id": "check-token-input", 
                "name": "token"
            }
        ),
        label="Введите название токена:",
    )
