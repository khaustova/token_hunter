import logging
from token_hunter.models import Settings
from token_hunter.src.utils.preprocessing_data import (
    count_no_operation, 
    count_pnl_loss, 
    get_sum_of_operation
)
from token_hunter.src.utils.tokens_data import (
    get_pairs_data,
    get_social_data,
    get_token_age,
)

logger = logging.getLogger(__name__)


class TokenChecker:
    """Класс для проверки токена на соответствие одной из настроек выбора токена.
    
    Attributes:
        pair: Адрес пары токенов для проверки.
        check_settings: Словарь с ID настроек и их функциями проверки токена.
    """

    def __init__(self, pair: str, check_settings: dict):
        """Инициализирует экземпляр TokenChecker.

        Args:
            pair: Адрес пары токенов для проверки.
            check_settings: Словарь с ID настроек и их функциями проверки токена в формате:
            {
                settings_id: {
                    "token_data": [список функций проверки],
                    "snipers_data": [список функций проверки],
                    "top_traders_data": [список функций проверки]
                }
            }
        """
        self.pair = pair
        self.check_settings = check_settings

    def check_token(
        self,
        snipers_data: dict | None=None,
        top_traders_data: dict| None=None,
        holders_data: dict| None=None
    ) -> int | None:
        """Проверяет токен на соответствие одной из настроек выбора токена.
        
        Note:
            Каждая функция проверки должна возвращать bool:
            - True: проверка пройдена
            - False: проверка не пройдена

        Args:
            snipers_data: Данные о снайперах. По умолчанию None.
            top_traders_data: Данные о топовых кошельках. По умолчанию None.
            holders_data: Данные о держателях токенов. По умолчанию None.

        Returns:
            ID настроек, которым соответствует токен, или None если не соответствует 
            ни одной из настроек.

        """
        token_data = get_pairs_data(self.pair)[0]

        is_check = True
        try:
            for settings_id, check in self.check_settings.items():

                for data_type, functions in check.items():

                    if not is_check:
                        break

                    if data_type == "token_data":
                        check_data = token_data
                    elif data_type == "snipers_data":
                        check_data = snipers_data
                    else:
                        check_data = top_traders_data

                    for function in functions:
                        data = function["get_data_value"](check_data)
                        is_check = function["check_data"](data)

                        if not is_check:
                            break

                if is_check:
                    return settings_id

                is_check = True
        except Exception:
            logger.exception("При проверке токена что-то пошло не так")

        return None


class CheckSettings:
    """Класс для работы с настройками выбора токенов."""
    
    def __init__(self, settings_id):
        """Инициализирует экземпляр CheckSettings.
        
        Args:
            settings_id: ID настроек из базы данных.
        """
        self.settings = Settings.objects.get(id=settings_id)
        
    def get_check_functions(self) -> dict:
        """Возвращает словарь с функциями проверки для разных типов данных токена.
        
        Returns:
            dict: Словарь с функциями проверки в формате:
                {
                    "token_data": [список функций проверки],
                    "snipers_data": [список функций проверки], 
                    "top_traders_data": [список функций проверки]
                }
        """
        check_functions = {
            "token_data": self.get_check_token_data(),
            "snipers_data": self.get_check_snipers_data(),
            "top_traders_data": self.get_check_top_traders_data()
        }
        
        return check_functions

    def get_check_token_data(self) -> list[dict]:
        """Создаёт список функций проверки токена для данных, полученных через DEX Screener API.
        
        Note:
            Функции проверки проверяют следующие параметры:
            - Цена
            - Возраст
            - Количество покупок/продаж за разные периоды
            - Объем торгов
            - Изменение цены
            - Ликвидность
            - FDV
            - Рыночная капитализация
            - Boost
            - Наличие соцсетей
        
        Returns:
            list: Список словарей с функциями проверки, каждый содержит:
                - check_data: функция проверки условия
                - get_data_value: функция получения значения из данных токена
                - settings_value: значение из настроек для сравнения
        """
        check_token_data = [
            # Цена токена: 
            {
                "check_data": lambda data_value: data_value >= self.settings.price_min,
                "get_data_value": lambda token_data: float(token_data["priceUsd"]),
                "settings_value": self.settings.price_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_max,
                "get_data_value": lambda token_data: float(token_data["priceUsd"]),
                "settings_value": self.settings.price_max
            },
            
            # Возраст токена:
            {
                "check_data": lambda data_value: data_value >= self.settings.token_age_min,
                "get_data_value": lambda token_data: get_token_age(token_data["pairCreatedAt"]),
                "settings_value": self.settings.token_age_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.token_age_max,
                "get_data_value": lambda token_data: get_token_age(token_data["pairCreatedAt"]),
                "settings_value": self.settings.token_age_max
            },
            
            # Количество покупок и продаж:
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_m5_min,
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["buys"],
                "settings_value": self.settings.buys_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_m5_max,             
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["buys"],
                "settings_value": self.settings.buys_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_m5_min,
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["sells"],
                "settings_value": self.settings.sells_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_m5_max,
                "get_data_value": lambda token_data: token_data["txns"]["m5"]["sells"],
                "settings_value": self.settings.sells_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_h1_min,
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["buys"],
                "settings_value": self.settings.buys_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_h1_max,             
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["buys"],
                "settings_value": self.settings.buys_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_h1_min,
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["sells"],
                "settings_value": self.settings.sells_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_h1_max,
                "get_data_value": lambda token_data: token_data["txns"]["h1"]["sells"],
                "settings_value": self.settings.sells_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_h6_min,
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["buys"],
                "settings_value": self.settings.buys_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_h6_max,             
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["buys"],
                "settings_value": self.settings.buys_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_h6_min,
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["sells"],
                "settings_value": self.settings.sells_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_h6_max,
                "get_data_value": lambda token_data: token_data["txns"]["h6"]["sells"],
                "settings_value": self.settings.sells_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.buys_h24_min,
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["buys"],
                "settings_value": self.settings.buys_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.buys_h24_max,             
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["buys"],
                "settings_value": self.settings.buys_h24_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sells_h24_min,
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["sells"],
                "settings_value": self.settings.sells_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sells_h24_max,
                "get_data_value": lambda token_data: token_data["txns"]["h24"]["sells"],
                "settings_value": self.settings.sells_h24_max
            },
            
            # Объём:
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_m5_min,
                "get_data_value": lambda token_data: token_data["volume"]["m5"],
                "settings_value": self.settings.volume_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_m5_max,            
                "get_data_value": lambda token_data: token_data["volume"]["m5"],
                "settings_value": self.settings.volume_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_h1_min,
                "get_data_value": lambda token_data: token_data["volume"]["h1"],
                "settings_value": self.settings.volume_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_h1_max,            
                "get_data_value": lambda token_data: token_data["volume"]["h1"],
                "settings_value": self.settings.volume_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_h6_min,
                "get_data_value": lambda token_data: token_data["volume"]["h6"],
                "settings_value": self.settings.volume_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_h6_max,            
                "get_data_value": lambda token_data: token_data["volume"]["h6"],
                "settings_value": self.settings.volume_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.volume_h24_min,
                "get_data_value": lambda token_data: token_data["volume"]["h24"],
                "settings_value": self.settings.volume_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.volume_h24_max,            
                "get_data_value": lambda token_data: token_data["volume"]["h24"],
                "settings_value": self.settings.volume_h24_max
            },
            
            # Изменение цены:
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_m5_min,
                "get_data_value": lambda token_data: token_data["priceChange"]["m5"],
                "settings_value": self.settings.price_change_m5_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_m5_min,                
                "get_data_value": lambda token_data: token_data["priceChange"]["m5"],
                "settings_value": self.settings.price_change_m5_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_h1_min, 
                "get_data_value": lambda token_data: token_data["priceChange"]["h1"],
                "settings_value": self.settings.price_change_h1_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_h1_max,                
                "get_data_value": lambda token_data: token_data["priceChange"]["h1"],
                "settings_value": self.settings.price_change_h1_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_h6_min,
                "get_data_value": lambda token_data: token_data["priceChange"]["h6"],
                "settings_value": self.settings.price_change_h6_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_h6_max,                
                "get_data_value": lambda token_data: token_data["priceChange"]["h6"],
                "settings_value": self.settings.price_change_h6_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.price_change_h24_min,
                "get_data_value": lambda token_data: token_data["priceChange"]["h24"],
                "settings_value": self.settings.price_change_h24_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.price_change_h24_max,                
                "get_data_value": lambda token_data: token_data["priceChange"]["h24"],
                "settings_value": self.settings.price_change_h24_max
            },
            
            # Ликвидность:
            {
                "check_data": lambda data_value: data_value >= self.settings.liquidity_min,               
                "get_data_value": lambda token_data: token_data["liquidity"]["usd"],
                "settings_value": self.settings.liquidity_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.liquidity_max,                
                "get_data_value": lambda token_data: token_data["liquidity"]["usd"],
                "settings_value": self.settings.liquidity_max
            },
            
            # FDV:
            {
                "check_data": lambda data_value: data_value >= self.settings.fdv_min,                
                "get_data_value": lambda token_data: token_data["fdv"],
                "settings_value": self.settings.fdv_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.fdv_max,            
                "get_data_value": lambda token_data: token_data["fdv"],
                "settings_value": self.settings.fdv_max
            },
            
            # Рыночная капитализация:
            {
                "check_data": lambda data_value: data_value >= self.settings.market_cap_min,                
                "get_data_value": lambda token_data: token_data["marketCap"],
                "settings_value": self.settings.market_cap_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.market_cap_max,                
                "get_data_value": lambda token_data: token_data["marketCap"],
                "settings_value": self.settings.market_cap_max
            },
            
            # Boost:
            {
                "check_data": lambda data_value: data_value >= self.settings.boost_min,                
                "get_data_value": lambda token_data: token_data["boosts"].get("active"),
                "settings_value": self.settings.boost_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.boost_max,                
                "get_data_value": lambda token_data: token_data["boosts"].get("active"),
                "settings_value": self.settings.boost_max
            },
            
            # Социальные сети:
            {
                "check_data": lambda social_data: any(social_data.values()),                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_socio
            },
            {
                "check_data": lambda social_data: social_data["is_telegram"],                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_telegram
            },
            {
                "check_data": lambda social_data: social_data["is_twitter"],                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_twitter
            },
            {
                "check_data": lambda social_data: social_data["is_website"],                
                "get_data_value": get_social_data,
                "settings_value": self.settings.is_website
            },

        ]

        return self.get_check_data(check_token_data)

    def get_check_snipers_data(self) -> list[dict]:
        """Создаёт список функций проверки транзакций снайперов токена.
        
        Note:
            Функции проверки проверяют следующие параметры:
            - Количество токенов у снайперов
            - Сумма покупок снайперов
            - Сумма продаж снайперов
            - Количество отрицательных PNL у снайперов
            - Снайперы без продажи или без покупки
        
        Returns:
            list: Список словарей с функциями проверки, каждый содержит:
                - check_data: функция проверки условия
                - get_data_value: функция получения значения из данных токена
                - settings_value: значение из настроек для сравнения
        """
        check_snipers_data = [
            # Количество токенов у снайперов:
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_held_all_min,
                "get_data_value": lambda snipers_data: snipers_data["held_all"],
                "settings_value": self.settings.sns_held_all_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_held_all_max,
                "get_data_value": lambda snipers_data: snipers_data["held_all"],
                "settings_value": self.settings.sns_held_all_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_sold_some_min,
                "get_data_value": lambda snipers_data: snipers_data["sold_some"],
                "settings_value": self.settings.sns_sold_some_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_sold_some_max,
                "get_data_value": lambda snipers_data: snipers_data["sold_some"],
                "settings_value": self.settings.sns_sold_some_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_sold_all_min,
                "get_data_value": lambda snipers_data: snipers_data["sold_all"],
                "settings_value": self.settings.sns_sold_all_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_sold_all_max,
                "get_data_value": lambda snipers_data: snipers_data["sold_all"],
                "settings_value": self.settings.sns_sold_all_max
            },

            # Сумма покупок снайперов:
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_bought_sum_min,
                "get_data_value": lambda snipers_data: get_sum_of_operation(snipers_data["bought"]),
                "settings_value": self.settings.sns_bought_sum_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_bought_sum_max,
                "get_data_value": lambda snipers_data: get_sum_of_operation(snipers_data["bought"]),
                "settings_value": self.settings.sns_bought_sum_max
            },

            # Сумма продаж снайперов:
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_sold_sum_min,
                "get_data_value": lambda snipers_data: get_sum_of_operation(snipers_data["sold"]),
                "settings_value": self.settings.sns_sold_sum_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_sold_sum_max,
                "get_data_value": lambda snipers_data: get_sum_of_operation(snipers_data["sold"]),
                "settings_value": self.settings.sns_sold_sum_max
            },

            # Количество отрицательных PNL у снайперов:
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_pnl_loss_min,
                "get_data_value": lambda snipers_data: count_pnl_loss(snipers_data["bought"], snipers_data["sold"]),
                "settings_value": self.settings.sns_pnl_loss_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_pnl_loss_max,
                "get_data_value": lambda snipers_data: count_pnl_loss(snipers_data["bought"], snipers_data["sold"]),
                "settings_value": self.settings.sns_pnl_loss_max
            },

            # Снайперы без продажи или без покупки:
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_no_bought_min,
                "get_data_value": lambda snipers_data: count_no_operation(snipers_data["bought"]),
                "settings_value": self.settings.sns_no_bought_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_no_bought_max,
                "get_data_value": lambda snipers_data: count_no_operation(snipers_data["bought"]),
                "settings_value": self.settings.sns_no_bought_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.sns_no_sold_min,
                "get_data_value": lambda snipers_data: count_no_operation(snipers_data["sold"]),
                "settings_value": self.settings.sns_no_sold_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.sns_no_sold_max,
                "get_data_value": lambda snipers_data: count_no_operation(snipers_data["sold"]),
                "settings_value": self.settings.sns_no_sold_max
            },
        ]

        return self.get_check_data(check_snipers_data)

    def get_check_top_traders_data(self) -> list[dict]:
        """Создаёт список функций проверки транзакций топовых кошельков токена.
        
        Note:
            Функции проверки проверяют следующие параметры:
            - Сумма покупок топов
            - Сумма продаж топов
            - Количество отрицательных PNL у топов
            - Топы без продажи или без покупки
        
        Returns:
            list: Список словарей с функциями проверки, каждый содержит:
                - check_data: функция проверки условия
                - get_data_value: функция получения значения из данных токена
                - settings_value: значение из настроек для сравнения
        """
        check_top_traders_data = [
            # Сумма покупок топов:
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_bought_sum_min,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_bought_sum_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_bought_sum_max,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_bought_sum_max
            },
            
            # Сумма продаж топов:
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_sold_sum_min,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_sold_sum_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_sold_sum_max,
                "get_data_value": lambda top_traders_data: get_sum_of_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_sold_sum_max
            },

            # Количество отрицательных PNL у топов:
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_pnl_loss_min,
                "get_data_value": lambda top_traders_data: count_pnl_loss(top_traders_data["bought"], top_traders_data["sold"]),
                "settings_value": self.settings.tt_pnl_loss_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_pnl_loss_max,
                "get_data_value": lambda top_traders_data: count_pnl_loss(top_traders_data["bought"], top_traders_data["sold"]),
                "settings_value": self.settings.tt_pnl_loss_max
            },

            # Топы без продажи или без покупки:
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_no_bought_min,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_no_bought_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_no_bought_max,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["bought"]),
                "settings_value": self.settings.tt_no_bought_max
            },
            {
                "check_data": lambda data_value: data_value >= self.settings.tt_no_sold_min,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_no_sold_min
            },
            {
                "check_data": lambda data_value: data_value <= self.settings.tt_no_sold_max,
                "get_data_value": lambda top_traders_data: count_no_operation(top_traders_data["sold"]),
                "settings_value": self.settings.tt_no_sold_max
            },
        ]

        return self.get_check_data(check_top_traders_data)


    def get_check_data(self, check_settings: list) -> list:
        """Создаёт список функций проверки, которые соответствуют параметрам, установленным 
        в настройках.
        
        Args:
            check_settings: Список из всех доступных функций проверки.
            
        Returns:
            Список из функций проверки, соответствующих текущим настройкам.
        """
        check_functions = []
        for check in check_settings:
            if check["settings_value"]:
                check_functions.append(check)

        return check_functions
