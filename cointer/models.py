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
    OPEN = "open", "Открытая"
    CLOSED = "closed", "Закрытая"
   
 
class Type(models.TextChoices):
    """
    Модель статуса транзакции.
    """
    TEST = "test", "Тест"
    EMULATION = "emulation", "Эмуляция"
    REAL = "real", "Реальная"


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
    selling_price = models.FloatField(
        blank=True, 
        null=True,
        verbose_name="Цена продажи"
    )
    buying_coin_age = models.FloatField(
        verbose_name="Возраст на момент покупки"
    )
    selling_coin_age = models.FloatField(
        blank=True, 
        null=True,
        verbose_name="Возраст на момент продажи"
    )
    buying_transactions_buys_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (5 минут)"
    )
    buying_transactions_sells_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (5 минут)"
    )
    buying_transactions_buys_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (1 час)"
    )
    buying_transactions_sells_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (1 час)"
    )
    buying_total_transfers = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество трансферов на момент покупки"
    )
    buying_total_transactions = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество транзакций на момент покупки"
    )
    selling_transactions_buys_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (5 минут)"
    )
    selling_transactions_sells_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (5 минут)"
    )
    selling_transactions_buys_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (1 час)"
    )
    selling_transactions_sells_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (1 час)"
    )
    buying_volume_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (5 минут)"
    )
    selling_volume_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (5 минут)"
    )
    buying_volume_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (1 час)"
    )
    selling_volume_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (1 час)"
    )
    buying_price_change_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (5 минут)"
    )
    buying_price_change_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (1 час)"
    )
    selling_price_change_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (5 минут)"
    )
    selling_price_change_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (1 час)"
    )
    buying_liquidity = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Ликвидность на момент покупки (5 минут)"
    )
    selling_liquidity = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Ликвидность на момент продажи (5 минут)"
    )
    buying_fdv = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="FDV на момент покупки"
    )
    selling_fdv = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="FDV на момент продажи"
    )
    buying_market_cap = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Рыночная капитализация на момент покупки"
    )
    selling_market_cap = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Рыночная капитализация на момент продажи"
    )
    is_telegram = models.BooleanField(
        default=False,
        verbose_name="Наличие Телеграма"
    )
    is_twitter = models.BooleanField(
        default=False,
        verbose_name="Наличие Твиттера"
    )
    is_website = models.BooleanField(
        default=False,
        verbose_name="Наличие сайта"
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
    type = models.CharField(
        max_length=64,
        choices=Type.choices,
        default=Type.TEST,
        verbose_name='Тип'
    )
    
    
    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

    def __str__(self):
        return self.pair
    
