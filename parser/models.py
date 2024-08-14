from django.db import models

class TopTrader(models.Model):
    coin = models.CharField(
        max_length=256, 
        verbose_name='Монета'
    )
    maker = models.CharField(
        max_length=256, 
        verbose_name='Кошелёк'
    )
    network = models.CharField(
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
    
    class Meta:
        verbose_name = 'Топ трейдеры'
        verbose_name_plural = 'Топ трейдер'
    
    def __str__(self):
        return f'{self.trader}: {self.PNL}'
