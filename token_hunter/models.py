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
        verbose_name="Пара"
    )
    wallet_address = models.CharField(
        max_length=256, 
        verbose_name="Адрес кошелька"
    )
    chain = models.CharField(
        max_length=256, 
        default="Solana",
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
        return f"Кошелёк {self.wallet_address} c {self.PNL} на {self.token_name}"
   
 
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
    
    # Данные о токене:
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
    price_b = models.FloatField(
        verbose_name="Цена покупки"
    )
    price_s = models.FloatField(
        blank=True, 
        null=True,
        verbose_name="Цена продажи"
    )
    token_age_b = models.FloatField(
        verbose_name="Возраст на момент покупки"
    )
    token_age_s = models.FloatField(
        blank=True, 
        null=True,
        verbose_name="Возраст на момент продажи"
    )
    transfers_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество трансферов на момент покупки"
    )
    transactions_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество транзакций на момент покупки"
    )
    buys_m5_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (5 минут)"
    )
    sells_m5_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (5 минут)"
    )
    buys_h1_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (1 час)"
    )
    sells_h1_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (1 час)"
    )
    buys_h6_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (6 часов)"
    )
    sells_h6_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (6 часов)"
    )
    buys_h24_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (24 часа)"
    )
    sells_h24_b = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (24 часа)"
    )
    buys_m5_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (5 минут)"
    )
    sells_m5_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (5 минут)"
    )
    buys_h1_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (1 час)"
    )
    sells_h1_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (1 час)"
    )
    buys_h6_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (6 часов)"
    )
    sells_h6_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (6 часов)"
    )
    buys_h24_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (24 часа)"
    )
    sells_h24_s = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (24 часа)"
    )
    volume_m5_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (5 минут)"
    )
    volume_h1_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (1 час)"
    )
    volume_h6_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (6 часов)"
    )
    volume_h24_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (24 часа)"
    )
    volume_m5_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (5 минут)"
    )
    volume_h1_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (1 час)"
    )
    volume_h6_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (6 часов)"
    )
    volume_h24_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (24 часа)"
    )
    price_change_m5_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (5 минут)"
    )
    price_change_h1_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (1 час)"
    )
    price_change_h6_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (6 часов)"
    )
    price_change_h24_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (24 часа)"
    )
    price_change_m5_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (5 минут)"
    )
    price_change_h1_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (1 час)"
    )
    price_change_h6_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (6 часов)"
    )
    price_change_h24_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (24 часа)"
    )
    liquidity_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Ликвидность на момент покупки (5 минут)"
    )
    liquidity_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Ликвидность на момент продажи (5 минут)"
    )
    fdv_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="FDV на момент покупки"
    )
    fdv_s = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="FDV на момент продажи"
    )
    market_cap_b = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Рыночная капитализация на момент покупки"
    )
    market_cap_s = models.FloatField(
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
    # Данные о снайперах:
    sns_bought = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Покупки снайперов"
    )
    sns_sold = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Продажи снайперов"
    )
    sns_sum_bought = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Суммарная покупки снайперов"
    )
    sns_sum_sold = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Суммарная продажа снайперов"
    )
    sns_held_all = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, которые держат"
    )
    sns_sold_some = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие часть"
    )
    sns_sold_all = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие всё"
    )
    sns_bought_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие меньше, чем на 0.1$"
    )
    sns_bought_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие больше, чем на 5000$"
    )
    sns_sold_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие меньше, чем на 0.1$"
    )
    sns_sold_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие больше, чем на 5000$"
    )
    sns_pnl_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с PNL больше, чем 5000$"
    )
    sns_no_bought = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы без покупки"
    )
    sns_pnl_profit = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с положительным PNL"
    )
    sns_pnl_loss = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с отрицательным PNL"
    )
    # Данные о топовых кошельках:
    tt_bought = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Покупки топов"
    )
    tt_sold = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Продажи топов"
    )
    tt_sum_bought = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Суммарная покупка топов"
    )
    tt_sum_sold = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Суммарная продажа топов"
    )
    tt_bought_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие меньше, чем на 0.1$"
    )
    tt_bought_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие больше, чем на 5000$"
    )
    tt_sold_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие меньше, чем на 0.1$"
    )
    tt_sold_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие больше, чем на 5000$"
    )
    tt_pnl_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с PNL больше, чем 5000$"
    )
    tt_no_bought = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы без покупки"
    )
    tt_no_sold = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы без продажи"
    )
    tt_pnl_profit = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с положительным PNL"
    )
    tt_pnl_loss = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с отрицательным PNL"
    )
    # Итоговые данные:
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
    # Настройки режима:
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
    transactions_buys_h1_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество покупок (1 час)"
    )
    transactions_buys_h1_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество покупок (1 час)"
    )
    transactions_sells_h1_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество продаж (1 час)"
    )
    transactions_sells_h1_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество продаж (1 час)"
    )
    total_transfers_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество трансферов"
    )
    total_transfers_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество трансферов"
    )
    total_transactions_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество транзакций"
    )
    total_transactions_max = models.IntegerField(
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