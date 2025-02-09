from django.db import models
from django.db.models import Count 

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
    transaction_count = models.IntegerField(
        default=0,
        verbose_name="Количество транзакций"
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
  

class Mode(models.TextChoices):
    """
    Модель статуса транзакции.
    """
    DATA_COLLECTION = "data_collection", "Сбор данных"
    EMULATION = "emulation", "Эмуляция"
    BOOSTED = "boosted", "Boosted",
    REAL = "real", "Реальная покупка"


class MonitoringRule(models.TextChoices):
    """
    Модель правила мониторинга токенов.
    """
    BOOSTED = "boosted", "Boosted",
    FILTER = "filter", "Фильтр"


class Settings(models.Model):
    """
    Настройки покупки токенов.
    """
    name = models.CharField(
        max_length=512,
        verbose_name="Название"
    )
    
    # Основные настройки:
    monitoring_rule = models.CharField(
        max_length=64,
        choices=MonitoringRule.choices,
        default=MonitoringRule.BOOSTED,
        verbose_name="Правильно мониторинга токенов"
    )
    mode = models.CharField(
        max_length=64,
        choices=Mode.choices,
        default=Mode.BOOSTED,
        verbose_name="Режим"
    )
    
    # Цена токена:
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
    
    # Возраст токена:
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
    
    # Количество покупок и продаж:
    buys_m5_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество покупок (5 минут)"
    )
    buys_m5_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество покупок (5 минут)"
    )
    sells_m5_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество продаж (5 минут)"
    )
    sells_m5_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество продаж (5 минут)"
    )
    buys_h1_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество покупок (1 час)"
    )
    buys_h1_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество покупок (1 час)"
    )
    sells_h1_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество продаж (1 час)"
    )
    sells_h1_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество продаж (1 час)"
    )
    buys_h6_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество покупок (6 часов)"
    )
    buys_h6_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество покупок (6 часов)"
    )
    sells_h6_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество продаж (6 часов)"
    )
    sells_h6_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество продаж (6 часов)"
    )
    buys_h24_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество покупок (24 часа)"
    )
    buys_h24_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество покупок (24 часа)"
    )
    sells_h24_min = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное количество продаж (24 часа)"
    )
    sells_h24_max = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное количество продаж (24 часа)"
    )
    
    # Объём:
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
    volume_h1_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальный объём торгов (1 час)"
    )
    volume_h1_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальный объём торгов (1 час)"
    )
    volume_h6_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальный объём торгов (6 часов)"
    )
    volume_h6_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальный объём торгов (6 часов)"
    )
    volume_h24_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальный объём торгов (24 часа)"
    )
    volume_h24_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальный объём торгов (24 часа)"
    )
    
    # Изменение цены:
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
    price_change_h1_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное изменение цены (1 час)"
    )
    price_change_h1_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное изменение цены (1 час)"
    )
    price_change_h6_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное изменение цены (6 часов)"
    )
    price_change_h6_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное изменение цены (6 часов)"
    )
    price_change_h24_min = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Минимальное изменение цены (24 часа)"
    )
    price_change_h24_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальное изменение цены (24 часа)"
    )
    
    # Ликвидность:
    liquidity_min = models.FloatField(
        blank=True, 
        null=True, 
        default=1000,
        verbose_name="Минимальная ликвидность"
    )
    liquidity_max = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Максимальная ликвидность"
    )
    
    # FDV:
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
    
    # Рыночная капитализация:
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
    
    # Социальные сети:
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
    
    # Снайперы с токенами:
    sns_held_all_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество снайперов, которые держат"
    )
    sns_held_all_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество снайперов, которые держат"
    )
    sns_sold_some_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество снайперов, продавших часть"
    )
    sns_sold_some_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество снайперов, продавших часть"
    )
    sns_sold_all_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество снайперов, продавших всё"
    )
    sns_sold_all_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество снайперов, продавших всё"
    )
    
    # Сумма покупок снайперов:
    sns_bought_sum_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Минимальная сумма покупок снайперов"
    )
    sns_bought_sum_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Максимальная сумма покупок снайперов"
    )
    
    # Сумма продаж снайперов:
    sns_sold_sum_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Минимальная сумма продаж снайперов"
    )
    sns_sold_sum_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Максимальная сумма продаж снайперов"
    )
    
    # Количество отрицательных PNL у снайперов:
    sns_pnl_loss_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество отрицательных PNL у снайперов"
    )
    sns_pnl_loss_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество отрицательных PNL у снайперов"
    )
    
    # Снайперы без продажи или без покупки:
    sns_no_bought_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество снайперов без покупки"
    )
    sns_no_bought_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество снайперов без покупки"
    )
    sns_no_sold_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество снайперов без продажи"
    )
    sns_no_sold_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество снайперов без продажи"
    )
    
    # Сумма покупок топов:
    tt_bought_sum_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Минимальная сумма покупок топов"
    )
    tt_bought_sum_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Максимальная сумма покупок топов"
    )
    
    # Сумма продаж топов:
    tt_sold_sum_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Максимальная сумма продаж топов"
    )
    tt_sold_sum_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Максимальная сумма продаж топов"
    )
    
    # Количество отрицательных PNL у топов:
    tt_pnl_loss_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество отрицательных PNL у топов"
    )
    tt_pnl_loss_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество отрицательных PNL у топов"
    )
    
    # Топы без продажи или без покупки:
    tt_no_bought_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество снайперов без покупки"
    )
    tt_no_bought_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество снайперов без покупки"
    )
    tt_no_sold_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество снайперов без продажи"
    )
    tt_no_sold_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество снайперов без продажи"
    )
    
    # Boost:
    boost_min = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Минимальное количество boost"
    )
    boost_max = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Максимальное количество boost"
    )
    
    # Риски:
    take_profit = models.FloatField(
        default=60,
        verbose_name="Take Profit"
    )
    stop_loss = models.FloatField(
        default=-20,
        verbose_name="Stop Loss"
    )
    
    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"
        ordering = ['name']

    def __str__(self):
        return self.name
    

class Status(models.TextChoices):
    """
    Модель статуса транзакции.
    """
    OPEN = "open", "Открытая"
    CLOSED = "closed", "Закрытая"


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
    transfers = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество трансферов"
    )
    buys_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок (5 минут)"
    )
    sells_m5 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж (5 минут)"
    )
    buys_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок (1 час)"
    )
    sells_h1 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж (1 час)"
    )
    buys_h6 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок (6 часов)"
    )
    sells_h6 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж (6 часов)"
    )
    buys_h24 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество покупок (24 часа)"
    )
    sells_h24 = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Количество продаж (24 часа)"
    )
    volume_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов (5 минут)"
    )
    volume_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов (1 час)"
    )
    volume_h6 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов (6 часов)"
    )
    volume_h24 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Объём торгов (24 часа)"
    )
    price_change_m5 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены (5 минут)"
    )
    price_change_h1 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены (1 час)"
    )
    price_change_h6 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены (6 часов)"
    )
    price_change_h24 = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Изменение цены (24 часа)"
    )
    liquidity = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Ликвидность (5 минут)"
    )
    fdv = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="FDV"
    )
    market_cap = models.FloatField(
        blank=True, 
        null=True, 
        verbose_name="Рыночная капитализация"
    )
    is_mutable_metadata = models.BooleanField(
        blank=True, 
        null=True, 
        default=True,
        verbose_name="Изменяемые метаданные"
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
    boosts = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name="Буст"
    )
    boosts_ages = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Возраст на момент бустов"
    )
    dextscore = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name="DextScore"
    )
    telegram_members = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Количество подписчиков в Телеграме"
    )
    is_telegram_error = models.BooleanField(
        blank=True,
        null=True,
        default=False,
        verbose_name="Телеграм указан, но не существует"
    )
    twitter_days = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Возраст Твиттера (дни)"
    )
    twitter_tweets = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Количество постов в Твиттере"
    )
    twitter_followers = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Количество подписчиков в Твиттере"
    )
    twitter_smart_followers = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Количество известных подписчиков в Твиттере"
    )
    is_twitter_error = models.BooleanField(
        blank=True,
        null=True,
        default=False,
        verbose_name="Твиттер указан, но не существует"
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
    tt_unrealized = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Нереализованные токены топов"
    )
    tt_speed = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name="Скорость топов"
    )
    # Итоговые данные:
    PNL = models.DecimalField(
        blank=True, 
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name="PNL"
    )
    PNL_10 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 10 %"
    )
    PNL_20 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 20 %"
    )
    PNL_30 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 30 %"
    )
    PNL_40 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 40 %"
    )
    PNL_50 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 50 %"
    )
    PNL_100 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 100 %"
    )
    PNL_200 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL 200 %"
    )
    PNL_loss_10 = models.BooleanField(
        blank=True,
        null=True,
        verbose_name="PNL -10 %"
    )
    status = models.CharField(
        max_length=64,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name="Статус"
    )
    price_change_check = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Изменение цены"
    )
    
    # Настройки режима:
    mode = models.CharField(
        max_length=64,
        choices=Mode.choices,
        default=Mode.DATA_COLLECTION,
        verbose_name="Тип"
    )

    # Настройки транзакции
    settings = models.ForeignKey(
        Settings,
        on_delete=models.CASCADE,
        verbose_name="Настройки",
        blank=True,
        null=True,  
    )
 
    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

    def __str__(self):
        return self.pair
