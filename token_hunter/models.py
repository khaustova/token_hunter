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
    buying_buys_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (5 минут)"
    )
    buying_sells_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (5 минут)"
    )
    buying_buys_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (1 час)"
    )
    buying_sells_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (1 час)"
    )
    buying_buys_h6 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (6 часов)"
    )
    buying_sells_h6 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (6 часов)"
    )
    buying_buys_h24 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент покупки (24 часа)"
    )
    buying_sells_h24 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент покупки (24 часа)"
    )
    selling_buys_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (5 минут)"
    )
    selling_sells_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (5 минут)"
    )
    selling_buys_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (1 час)"
    )
    selling_sells_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (1 час)"
    )
    selling_buys_h6 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (6 часов)"
    )
    selling_sells_h6 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (6 часов)"
    )
    selling_buys_h24 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок на момент продажи (24 часа)"
    )
    selling_sells_h24 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж на момент продажи (24 часа)"
    )
    buying_volume_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (5 минут)"
    )
    buying_volume_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (1 час)"
    )
    buying_volume_h6 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (6 часов)"
    )
    buying_volume_h24 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент покупки (24 часа)"
    )
    selling_volume_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (5 минут)"
    )
    selling_volume_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (1 час)"
    )
    selling_volume_h6 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (6 часов)"
    )
    selling_volume_h24 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов на момент продажи (24 часа)"
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
    buying_price_change_h6 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (6 часов)"
    )
    buying_price_change_h24 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент покупки (24 часа)"
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
    selling_price_change_h6 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (6 часов)"
    )
    selling_price_change_h24 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены на момент продажи (24 часа)"
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
    snipers_bought = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Покупки снайперов"
    )
    snipers_sold = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Продажи снайперов"
    )
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
    # Данные о снайперах:
    snipers_held_all = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, которые держат"
    )
    snipers_sold_some = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие часть"
    )
    snipers_sold_all = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие всё"
    )
    snipers_bought_N1 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 1-го снайпера"
    )
    snipers_sold_N1 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 1-го снайпера"
    )
    snipers_bought_N2 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 2-го снайпера"
    )
    snipers_sold_N2 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 2-го снайпера"
    )
    snipers_bought_N3 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 3-го снайпера"
    )
    snipers_sold_N3 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 3-го снайпера"
    )
    snipers_bought_N4 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 4-го снайпера"
    )
    snipers_sold_N4 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 4-го снайпера"
    )
    snipers_bought_N5 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 5-го снайпера"
    )
    snipers_sold_N5 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 5-го снайпера"
    )
    snipers_bought_N6 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 6-го снайпера"
    )
    snipers_sold_N6 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 6-го снайпера"
    )
    snipers_bought_N7 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 7-го снайпера"
    )
    snipers_sold_N7 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 7-го снайпера"
    )
    snipers_bought_N8 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 8-го снайпера"
    )
    snipers_sold_N8 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 8-го снайпера"
    )
    snipers_bought_N9 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 9-го снайпера"
    )
    snipers_sold_N9 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 9-го снайпера"
    )
    snipers_bought_N10 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Покупка 10-го снайпера"
    )
    snipers_sold_N10 = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Продажа 10-го снайпера"
    )
    snipers_bought_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие меньше, чем на 0.1$"
    )
    snipers_bought_100_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие меньше, чем на 100$"
    )
    snipers_bought_100_500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие на 100$ - 500$"
    )
    snipers_bought_500_1000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие на 500$ - 1000$"
    )
    snipers_bought_1000_2500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие на 1000$ - 2500$"
    )
    snipers_bought_2500_5000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие на 2500$ - 5000$"
    )
    snipers_bought_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, купившие больше, чем на 5000$"
    )
    snipers_sold_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие меньше, чем на 0.1$"
    )
    snipers_sold_100_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие меньше, чем на 100$"
    )
    snipers_sold_100_500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие на 100$ - 500$"
    )
    snipers_sold_500_1000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие на 500$ - 1000$"
    )
    snipers_sold_1000_2500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие на 1000$ - 2500$"
    )
    snipers_sold_2500_5000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие на 2500$ - 5000$"
    )
    snipers_sold_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы, продавшие больше, чем на 5000$"
    )
    snipers_pnl_100_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с PNL меньше, чем 100$"
    )
    snipers_pnl_100_500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с PNL 100$ - 500$"
    )
    snipers_pnl_500_1000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с PNL 500$ - 1000$"
    )
    snipers_pnl_1000_2500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с PNL 1000$ - 2500$"
    )
    snipers_pnl_2500_5000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с PNL 2500$ - 5000$"
    )
    snipers_pnl_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с PNL больше, чем 5000$"
    )
    snipers_no_bought = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы без покупки"
    )
    snipers_pnl_profit = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с положительным PNL"
    )
    snipers_pnl_loss = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Снайперы с отрицательным PNL"
    )
    # Данные о топовых кошельках:
    top_traders_bought_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие меньше, чем на 0.1$"
    )
    top_traders_bought_100_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие меньше, чем на 100$"
    )
    top_traders_bought_100_500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие на 100$ - 500$"
    )
    top_traders_bought_500_1000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие на 500$ - 1000$"
    )
    top_traders_bought_1000_2500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие на 1000$ - 2500$"
    )
    top_traders_bought_2500_5000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие на 2500$ - 5000$"
    )
    top_traders_bought_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, купившие больше, чем на 5000$"
    )
    top_traders_sold_01_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие меньше, чем на 0.1$"
    )
    top_traders_sold_100_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие меньше, чем на 100$"
    )
    top_traders_sold_100_500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие на 100$ - 500$"
    )
    top_traders_sold_500_1000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие на 500$ - 1000$"
    )
    top_traders_sold_1000_2500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие на 1000$ - 2500$"
    )
    top_traders_sold_2500_5000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие на 2500$ - 5000$"
    )
    top_traders_sold_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы, продавшие больше, чем на 5000$"
    )
    top_traders_pnl_100_less = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с PNL меньше, чем на 100$"
    )
    top_traders_pnl_100_500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с PNL 100$ - 500$"
    )
    top_traders_pnl_500_1000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с PNL 500$ - 1000$"
    )
    top_traders_pnl_1000_2500 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с PNL 1000$ - 2500$"
    )
    top_traders_pnl_2500_5000 = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с PNL 2500$ - 5000$"
    )
    top_traders_pnl_5000_more = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с PNL больше, чем 5000$"
    )
    top_traders_no_bought = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы без покупки"
    )
    top_traders_no_sold = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы без продажи"
    )
    top_traders_pnl_profit = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Топы с положительным PNL"
    )
    top_traders_pnl_loss = models.IntegerField(
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