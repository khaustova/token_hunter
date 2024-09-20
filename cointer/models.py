from django.db import models


class TopTrader(models.Model):
    """
    Модель данных c топ кошельками.
    """
    coin = models.CharField(
        max_length=256, 
        verbose_name='Монета'
    )
    coin_address = models.CharField(
        max_length=256, 
        verbose_name='Адрес монеты'
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
   
 
class Status(models.TextChoices):
    """
    Модель статуса транзакции.
    """
    OPEN = 'open', 'Открытая'
    CLOSED = 'closed', 'Закрытая' 


class Transaction(models.Model):
    """ 
    Модель данных транзакций.
    """
    pair = models.CharField(
        max_length=256, 
        verbose_name='Pair'
    )
    coin = models.CharField(
        verbose_name="Монета", 
        max_length=256
    )
    coin_address = models.CharField(
        verbose_name="Адрес", 
        max_length=256
    )
    buying_price = models.FloatField(
        verbose_name="Цена покупки"
    )
    current_price = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Текущая цена"
    )
    selling_price = models.FloatField(
        blank=True, 
        null=True,
        verbose_name="Цена продажи"
    )
    opening_date = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Время покупки"
    )
    closing_date = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Время продажи"
    )
    PNL = models.DecimalField(
        blank=True, 
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name="PNL"
    )
    status = models.CharField(
        max_length=64,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='Статус'
    )
    
    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

    def __str__(self):
        return self.pair
