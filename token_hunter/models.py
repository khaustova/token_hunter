from django.db import models


class TopTrader(models.Model):
    """
    Модель данных c топ кошельками.
    """
    token_name = models.CharField(
        max_length=256,
        verbose_name="Название токена"
    )
    token_address = models.CharField(
        max_length=256, 
        verbose_name="Адрес токена"
    )
    pair = models.CharField(
        max_length=256, 
        verbose_name="Pair"
    )
    maker = models.CharField(
        max_length=256, 
        verbose_name="Кошелёк"
    )
    chain = models.CharField(
        max_length=256, 
        verbose_name="Сеть"
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
        return f"Кошелёк {self.maker} c {self.PNL} на {self.token_name}"
   
 
class Status(models.TextChoices):
    """
    Модель статуса транзакции.
    """
    OPEN = "open", "Открытая"
    CLOSED = "closed", "Закрытая"
   
 
class Mode(models.TextChoices):
    """
    Модель статуса транзакции.
    """
    DATA_COLLECTION = "data_collection", "Сбор данных"
    EMULATION = "emulation", "Эмуляция"
    REAL = "real", "Реальная покупка"


class Transaction(models.Model):
    """ 
    Модель данных транзакций.
    """
    pair = models.CharField(
        max_length=256, 
        verbose_name='Pair'
    )
    token_name = models.CharField(
        verbose_name="Имя токена", 
        max_length=256
    )
    token_address = models.CharField(
        verbose_name="Адрес токена", 
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
    buying_token_age = models.FloatField(
        verbose_name="Возраст на момент покупки"
    )
    selling_token_age = models.FloatField(
        blank=True, 
        null=True,
        verbose_name="Возраст на момент продажи"
    )
    buying_transactions_buys_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (5 минут)"
    )
    buying_transactions_sells_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (5 минут)"
    )
    buying_transactions_buys_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (1 час)"
    )
    buying_transactions_sells_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (1 час)"
    )
    buying_total_transfers = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество трансферов на момент покупки"
    )
    buying_total_transactions = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество транзакций на момент покупки"
    )
    selling_transactions_buys_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (5 минут)"
    )
    selling_transactions_sells_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (5 минут)"
    )
    selling_transactions_buys_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (1 час)"
    )
    selling_transactions_sells_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (1 час)"
    )
    buying_volume_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (5 минут)"
    )
    selling_volume_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (5 минут)"
    )
    buying_volume_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (1 час)"
    )
    selling_volume_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (1 час)"
    )
    buying_price_change_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (5 минут)"
    )
    buying_price_change_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (1 час)"
    )
    selling_price_change_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (5 минут)"
    )
    selling_price_change_h1 = models.FloatField(
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
        verbose_name="Статус"
    )
    mode = models.CharField(
        max_length=64,
        choices=Mode.choices,
        default=Mode.DATA_COLLECTION,
        verbose_name="Тип"
    )
    
    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

    def __str__(self):
        return self.pair
    

class Settings(models.Model):
    filter = models.CharField(
        max_length=1024,
        default="?rankBy=trendingScoreH6&order=desc&minLiq=1000&maxAge=1",
        verbose_name="Фильтр по умолчанию"
    )
    price_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальная стоимость"
    )
    price_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальная стоимость"
    )
    token_age_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальный возраст"
    )
    token_age_max = models.FloatField(
        blank=True, 
        null=True, 
        default=5,
        verbose_name="Максимальный возраст"
    )
    transactions_buys_h1_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество покупок (1 час)"
    )
    transactions_buys_h1_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество покупок (1 час)"
    )
    transactions_sells_h1_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество продаж (1 час)"
    )
    transactions_sells_h1_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество продаж (1 час)"
    )
    total_transfers_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество трансферов"
    )
    total_transfers_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество трансферов"
    )
    total_transactions_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество транзакций"
    )
    total_transactions_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество транзакций"
    )
    volume_m5_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальный объём торгов (5 минут)"
    )
    volume_m5_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальный объём торгов (5 минут)"
    )
    price_change_m5_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное изменение цены (5 минут)"
    )
    price_change_m5_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное изменение цены (5 минут)"
    )
    liquidity_min = models.FloatField(
        blank=True, 
        null=True, 
        default=1000,
        verbose_name="Минимальная ликвидность (5 минут)"
    )
    liquidity_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальная ликвидность (5 минут)"
    )
    fdv_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальная FDV"
    )
    fdv_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальная FDV"
    )
    market_cap_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальная рыночная капитализация"
    )
    market_cap_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальная рыночная капитализация"
    )
    is_socio = models.BooleanField(
        default=False,
        verbose_name="Наличие хотя бы одной социальной сети или сайта"
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
    take_profit = models.FloatField(
        default=60,
        verbose_name="Take Profit"
    )
    stop_loss = models.FloatField(
        default=-20,
        verbose_name="Stop Loss"
    )
    mode = models.CharField(
        max_length=64,
        choices=Mode.choices,
        default=Mode.DATA_COLLECTION,
        verbose_name="Режим"
    )
    
    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Настройки"