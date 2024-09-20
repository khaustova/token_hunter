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
        label="Введите фильтр для поиска монет:",
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
    
class CheckCoinForm(forms.Form): 
    """
    Форма для базовой проверки монеты.
    """
     
    coin = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Сейчас поддерживается только сеть SOLANA", 
                "id": "check-coin-input", 
                "name": "coin"
            }
        ),
        label="Введите название монеты:",
    )
