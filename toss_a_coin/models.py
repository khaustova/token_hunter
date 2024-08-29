from django.db import models
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType

class TopTrader(models.Model):
    """
    Модель данных о топ кошельках.
    """
    
    coin = models.CharField(
        max_length=256, 
        verbose_name='Монета'
    )
    pair = models.CharField(
        max_length=256, 
        verbose_name='Pair'
    )
    maker = models.CharField(
        max_length=256, 
        verbose_name='Кошелёк'
    )
    chain = models.CharField(
        max_length=256, 
        verbose_name='Сеть'
    )
    bought = models.IntegerField(
        verbose_name="Купил"
    )
    sold = models.IntegerField(
        verbose_name="Продал"
    )
    PNL = models.FloatField(
        verbose_name="PNL"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Топ кошельков"
        verbose_name_plural = "Топ кошельков"

    def __str__(self):
        return f"Кошелёк {self.maker} c {self.PNL} на {self.coin}"
